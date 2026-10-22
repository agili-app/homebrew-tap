"""Validate staged catalogs and adapt native updater artifacts."""
from dataclasses import dataclass
import io
import json
from pathlib import Path
from urllib.parse import urlparse, unquote
import zipfile

from common import ReleaseError, digest, public_artifact_url, version, validate_build_seq, validate_minimum_system_version


@dataclass
class PreparedTarget:
    files: dict[str, bytes]
    downloads: list[dict]
    updates: list[dict]
    assets: list[dict]
    native: dict | None
    notes: str


def _metrix_build_seq(value):
    if type(value) is not int:
        raise ReleaseError('Metrix.Bar buildSeq must be an integer')
    validate_build_seq(value)
    return value


def prepare_target(product, prefix, base, record, row, bundle):
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        catalog = json.loads(archive.read('artifacts.json'))
        for key, expected in [('schemaVersion', 1), ('product', product),
                              ('platform', row['platform']), ('arch', row['arch']),
                              ('updateVersion', record['updateVersion'])]:
            if catalog.get(key) != expected:
                raise ReleaseError('catalog does not match reservation: ' + key)
        if product == 'metrix-bar':
            if _metrix_build_seq(catalog.get('buildSeq')) != _metrix_build_seq(record.get('buildSeq')):
                raise ReleaseError('catalog does not match reservation: buildSeq')
        notes = catalog.get('notes')
        if notes is None and product == 'metrix-bar':
            notes = json.loads(archive.read(catalog['mygoManifestPath'])).get('notes')
        if not isinstance(notes, str) or not notes.strip():
            raise ReleaseError('catalog requires nonempty release notes')
        files, downloads, updates, assets = {}, [], [], []
        def artifact(path):
            if not path or Path(path).is_absolute() or '..' in Path(path).parts or '\\' in path:
                raise ReleaseError('unsafe catalog path')
            data = archive.read(path)
            name = Path(path).name
            key = f'{record.get("artifactPrefix", prefix + "/releases")}/{record.get("artifactPath", record["updateVersion"])}/{row["platform"]}-{row["arch"]}/{name}'
            if key in files and files[key] != data:
                raise ReleaseError('duplicate artifact basename')
            files[key] = data
            return {'name': name, 'url': public_artifact_url(base, key, prefix),
                    'size': len(data), 'sha256': digest(data), 'key': key}
        for entry in catalog['artifacts']:
            if entry['kind'] not in {'installer', 'update'} or entry['format'] not in {'dmg', 'zip', 'exe', 'tar.gz', 'deb', 'appimage'}:
                raise ReleaseError('invalid artifact kind/format')
            info = {**artifact(entry['path']), 'platform': row['platform'], 'arch': row['arch'], 'format': entry['format']}
            role = entry.get('role', 'gui')
            if role not in {'gui', 'cli'} or (role == 'cli' and (entry['kind'] == 'update' or entry.get('updater'))):
                raise ReleaseError('invalid artifact role or CLI updater')
            if 'role' in entry:
                info['role'] = role
            if not info['size']:
                raise ReleaseError('empty artifact')
            if row['platform'] == 'macos' and role == 'gui' and entry['kind'] == 'installer':
                validate_minimum_system_version(entry.get('minimumSystemVersion'))
            if entry.get('minimumSystemVersion'):
                info['minimumSystemVersion'] = entry['minimumSystemVersion']
            if entry['kind'] == 'installer':
                downloads.append({k: v for k, v in info.items() if k != 'key'})
            if entry['kind'] == 'update' or entry.get('updater'):
                updates.append(info)
                if product == 'metrix-bar':
                    for delta in entry.get('deltas', []):
                        artifact(delta['path'])
                        if delta.get('signaturePath'):
                            artifact(delta['signaturePath'])
                if product == 'tinymd':
                    signature = artifact(entry['signaturePath'])
                    info.update(signatureKey=signature['key'], signatureSha256=signature['sha256'])
                    asset = {k: info[k] for k in ('name', 'url', 'size', 'arch', 'format', 'sha256')}
                    asset.update(os=row['platform'], signature_url=signature['url'], deltas=[])
                    for delta in entry.get('deltas', []):
                        if delta['format'] != 'files-bsdiff-v1' or version(delta['from']) >= version(record['updateVersion']):
                            raise ReleaseError('invalid delta baseline')
                        d = artifact(delta['path'])
                        sig = artifact(delta['signaturePath'])
                        asset['deltas'].append({**{k: d[k] for k in ('name', 'url', 'size', 'sha256')},
                                               'from': delta['from'], 'to': record['updateVersion'],
                                               'signature_url': sig['url'], 'format': 'files-bsdiff-v1'})
                    if len(asset['deltas']) > 3 or (row['platform'] == 'windows' and asset['deltas']):
                        raise ReleaseError('unsupported delta matrix')
                    assets.append(asset)
        if not downloads or not updates:
            raise ReleaseError('target needs an installer and updater payload')
        native = None
        if product == 'metrix-bar':
            native = json.loads(archive.read(catalog['mygoManifestPath']))
            if _metrix_build_seq(native.get('buildSeq')) != record['buildSeq']:
                raise ReleaseError('native MyGO manifest does not match reservation: buildSeq')
            native['notes'] = notes
            if native['version'] != record['updateVersion'] or not native.get('signature'):
                raise ReleaseError('invalid native MyGO manifest')
            def rewrite(item):
                name = unquote(Path(urlparse(item['url']).path).name)
                match = next((k for k in files if Path(k).name == name), None)
                if match is None:
                    match = artifact(name)['key']
                if len(files[match]) != item['size'] or not item.get('signature'):
                    raise ReleaseError('native manifest size/signature mismatch')
                item['url'] = public_artifact_url(base, match, prefix)
            rewrite(native)
            if native['url'] not in {a['url'] for a in updates}:
                raise ReleaseError('native update payload is absent from catalog')
            for previous in native.get('previous', []):
                allowed = [base + '/releases/'] + [
                    public_artifact_url(base, channel + '/' + prefix + '/releases/', prefix)
                    for channel in ('stable', 'preview')]
                path = unquote(urlparse(previous['url']).path)
                if (not any(previous['url'].startswith(root) for root in allowed)
                        or '..' in path.split('/') or '\\' in path):
                    raise ReleaseError('native previous archive must reference public immutable release')
            for delta in native.get('deltas', []):
                if version(delta['from']) >= version(record['updateVersion']):
                    raise ReleaseError('native delta baseline is not older')
                rewrite(delta)
            if len(native.get('deltas', [])) > 3:
                raise ReleaseError('too many native deltas')
            for info in updates:
                if info['url'] == native['url']:
                    info['nativeManifest'] = native
        return PreparedTarget(files, downloads, updates, assets, native, notes)


def bundle_directory(directory):
    catalog = json.loads((directory / 'artifacts.json').read_text())
    paths = {'artifacts.json'}
    for artifact in catalog['artifacts']:
        paths.add(artifact['path'])
        if artifact.get('signaturePath'):
            paths.add(artifact['signaturePath'])
        for delta in artifact.get('deltas', []):
            paths.add(delta['path'])
            if delta.get('signaturePath'):
                paths.add(delta['signaturePath'])
    if catalog.get('mygoManifestPath'):
        paths.add(catalog['mygoManifestPath'])
        native = json.loads((directory / catalog['mygoManifestPath']).read_text())
        for delta in native.get('deltas', []):
            name = unquote(Path(urlparse(delta['url']).path).name)
            if not any(Path(path).name == name for path in paths):
                raise ReleaseError('native delta must be listed in catalog')
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_STORED) as archive:
        for path in sorted(paths):
            source = (directory / path).resolve()
            if not source.is_relative_to(directory.resolve()):
                raise ReleaseError('artifact escapes output directory')
            archive.writestr(path, source.read_bytes())
    return stream.getvalue()
