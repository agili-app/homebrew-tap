"""Reservation, baseline selection and resumable release publication."""
import json
import re
from datetime import datetime, timezone
from email.message import Message

from artifacts import prepare_target
from common import PRODUCTS, DYNAMIC, IMMUTABLE, ReleaseError, digest, encoded, public_artifact_url, version, validate_build_seq


class Publisher:
    def __init__(self, store, product, base=None):
        self.store = store
        self.product = product
        self.prefix = PRODUCTS[product][1]
        self.base = (base or f'https://downloads.agili.app/{self.prefix}').rstrip('/')
        if not self.base.startswith('https://'):
            raise ReleaseError('public download base must be HTTPS')
        self.control = f'{self.prefix}/control.json'

    def state(self):
        data, etag = self.store.get(self.control, True)
        return (json.loads(data) if data else {'seq': 0, 'runs': {}, 'previews': {}, 'history': []}), etag

    def save(self, state, etag):
        self.store.put(self.control, encoded(state), True, etag=etag, absent=etag is None)

    def reservation(self, run):
        state, _ = self.state()
        return state['runs'][str(run)]

    def reserve(self, run, channel, requested, bump, sha, matrix, source_ref='main'):
        state, etag = self.state()
        run = str(run)
        if run in state['runs']:
            existing = state['runs'][run]
            if (existing['product'], existing['channel'], existing['sourceSha'], existing['matrix'], existing.get('requestedVersion', ''), existing.get('bump', 'patch'), existing.get('sourceRef', 'main')) != (self.product, channel, sha, matrix, requested, bump, source_ref):
                raise ReleaseError('retry reservation parameters differ')
            return existing
        highest = max([r['displayVersion'] for r in state['runs'].values()] or ['0.0.0'], key=version)
        base = requested
        if not base:
            base = str(getattr(version(highest), 'bump_' + bump)())
        if version(base).prerelease is not None:
            raise ReleaseError('display version must be X.Y.Z')
        frozen = [r['displayVersion'] for r in state['runs'].values() if r['channel'] == 'stable']
        if frozen and version(base) <= max(map(version, frozen)):
            raise ReleaseError('stable version is frozen; duplicate/downgrade rejected')
        if channel == 'stable':
            update = base
        else:
            number = state['previews'].get(base, 0) + 1
            state['previews'][base] = number
            update = f'{base}-preview.{number}'
        state['seq'] += 1
        validate_build_seq(state['seq'])
        record = {'runId': run, 'product': self.product, 'channel': channel,
                  'sourceSha': sha, 'sourceRef': source_ref, 'displayVersion': base, 'updateVersion': update,
                  'buildSeq': state['seq'], 'matrix': matrix, 'status': 'reserved',
                  'requestedVersion': requested, 'bump': bump,
                  'publishedAt': datetime.now(timezone.utc).isoformat()}
        state['runs'][run] = record
        self.save(state, etag)
        return record

    def stage_key(self, run, platform, arch):
        return f'{self.prefix}/runs/{run}/{platform}-{arch}.zip'

    def stage(self, run, platform, arch, data):
        key = self.stage_key(run, platform, arch)
        old, _ = self.store.get(key, True)
        if old is not None and old != data:
            raise ReleaseError('signed stage collision; retry must reuse existing bundle')
        if old is None:
            self.store.put(key, data, True, absent=True)

    def immutable(self, key, data):
        if '\r' in key or '\n' in key:
            raise ReleaseError('invalid attachment filename')
        filename = re.sub(r'[^A-Za-z0-9._-]', '_', key.rsplit('/', 1)[-1]) or 'download'
        header = Message()
        header.add_header('Content-Disposition', 'attachment', filename=filename)
        old, etag = self.store.get(key)
        if old is not None and old != data:
            raise ReleaseError('immutable artifact collision')
        # Reapply metadata to identical objects from interrupted/older publishers.
        self.store.put(key, data, etag=etag, absent=old is None, cache=IMMUTABLE,
                       disposition=header['Content-Disposition'])
        self.store.verify_public(public_artifact_url(self.base, key.removeprefix(self.prefix + '/')), data)

    def baseline(self, run, platform, arch, directory):
        state, _ = self.state()
        current = version(state['runs'][str(run)]['updateVersion'])
        history = sorted(state['history'], key=lambda r: (version(r['updateVersion']), r['buildSeq']), reverse=True)
        result, counts = [], {}
        for previous in history:
            if version(previous['updateVersion']) >= current:
                continue
            for item in previous['updates']:
                format = item['format']
                if (item['platform'], item['arch']) != (platform, arch) or counts.get(format, 0) >= 3:
                    continue
                counts[format] = counts.get(format, 0) + 1
                data, _ = self.store.get(item['key'])
                if data is None or digest(data) != item['sha256']:
                    raise ReleaseError('baseline missing or digest mismatch')
                path = directory / (previous['updateVersion'] + '-' + item['name'])
                path.write_bytes(data)
                baseline = {**{k: item[k] for k in ('platform', 'arch', 'format', 'sha256', 'url')},
                            'updateVersion': previous['updateVersion'], 'path': str(path.resolve())}
                if item.get('signatureKey'):
                    signature, _ = self.store.get(item['signatureKey'])
                    if signature is None or digest(signature) != item['signatureSha256']:
                        raise ReleaseError('baseline signature missing or digest mismatch')
                    signature_path = directory / (path.name + '.minisig')
                    signature_path.write_bytes(signature)
                    baseline['signaturePath'] = str(signature_path.resolve())
                if item.get('nativeManifest'):
                    baseline['nativeManifest'] = item['nativeManifest']
                result.append(baseline)
        return result

    def prepare(self, record, row, bundle):
        return prepare_target(self.product, self.prefix, self.base, record, row, bundle)

    def needs_build(self, run, platform, arch):
        record = self.reservation(run)
        row = next((row for row in record['matrix'] if (row['platform'], row['arch']) == (platform, arch)), None)
        if row is None:
            raise ReleaseError('target does not match reservation')
        bundle, _ = self.store.get(self.stage_key(run, platform, arch), True)
        if bundle is None:
            return True
        self.prepare(record, row, bundle)
        return False

    def publish(self, run):
        state, etag = self.state()
        record = state['runs'][str(run)]
        if record['status'] == 'published':
            return record['releaseInfo']
        public_data, _ = self.store.get(f'{self.prefix}/release-info.json')
        public_info = json.loads(public_data) if public_data else None
        current = public_info['channels'].get(record['channel']) if public_info else None
        if current and (current['buildSeq'] > record['buildSeq'] or version(current['updateVersion']) > version(record['updateVersion'])):
            raise ReleaseError('superseded reservation cannot advance mutable release metadata')
        prepared = []
        for row in record['matrix']:
            bundle, _ = self.store.get(self.stage_key(run, row['platform'], row['arch']), True)
            if bundle is None:
                raise ReleaseError('incomplete platform matrix')
            prepared.append((row, self.prepare(record, row, bundle)))
        all_notes = {item.notes for _, item in prepared}
        if len(all_notes) != 1:
            raise ReleaseError('platform release notes must match')
        record['notes'] = next(iter(all_notes))
        # No mutable object changes until the complete matrix validates and all immutable bytes are reachable.
        for _, item in prepared:
            for key, data in item.files.items():
                self.immutable(key, data)
        downloads = [a for _, item in prepared for a in item.downloads]
        updates = [a for _, item in prepared for a in item.updates]
        info_data, _ = self.store.get(f'{self.prefix}/release-info.json')
        info = json.loads(info_data) if info_data else {'schemaVersion': 1, 'product': self.product, 'channels': {'stable': None, 'preview': None}, 'history': []}
        release = {k: record[k] for k in ('displayVersion', 'updateVersion', 'channel', 'buildSeq', 'publishedAt')}
        release.update(notes=record.get('notes', ''), downloads=downloads)
        highwaters = state.setdefault('channels', {})
        # Seed older control records from the public index before claiming a channel.
        for channel, live in info['channels'].items():
            if live and channel not in highwaters:
                highwaters[channel] = {'runId': None, 'updateVersion': live['updateVersion'], 'buildSeq': live['buildSeq']}
        channels = record.get('publishingChannels')
        if channels is not None:
            if highwaters.get(record['channel'], {}).get('runId') != str(run):
                raise ReleaseError('superseded reservation lost its target channel owner')
            channels = [channel for channel in channels if highwaters.get(channel, {}).get('runId') == str(run)]
        if channels is None:
            channels = [record['channel']]
            preview = highwaters.get('preview')
            if record['channel'] == 'stable' and (preview is None or version(record['updateVersion']) > version(preview['updateVersion'])):
                channels.append('preview')
        for channel in channels:
            watermark = highwaters.get(channel)
            if watermark and watermark['runId'] != str(run) and (watermark['buildSeq'] >= record['buildSeq'] or version(watermark['updateVersion']) >= version(record['updateVersion'])):
                raise ReleaseError('superseded reservation cannot advance mutable release metadata')
        record['publishingChannels'] = channels
        progress = record.setdefault('mutableObjects', {})
        for channel in channels:
            highwaters[channel] = {'runId': str(run), 'updateVersion': record['updateVersion'], 'buildSeq': record['buildSeq']}
        # Persist ownership and all channel highwaters before the first mutable PUT.
        self.save(state, etag)
        state, etag = self.state()
        record = state['runs'][str(run)]
        progress = record['mutableObjects']

        def mutable(key, payload):
            nonlocal state, etag, record, progress
            checksum = digest(encoded(payload))
            if progress.get(key) == {'sha256': checksum, 'status': 'done'}:
                return
            progress[key] = {'sha256': checksum, 'status': 'writing'}
            self.save(state, etag)
            state, etag = self.state()
            record = state['runs'][str(run)]
            progress = record['mutableObjects']
            self.store.put(key, encoded(payload), cache=DYNAMIC)
            progress[key]['status'] = 'done'
            self.save(state, etag)
            state, etag = self.state()
            record = state['runs'][str(run)]
            progress = record['mutableObjects']

        for channel in channels:
            if self.product == 'tinymd':
                feed = {'schema_version': 1, 'version': record['updateVersion'], 'notes': release['notes'],
                        'assets': [a for _, item in prepared for a in item.assets]}
                mutable(f'{self.prefix}/feeds/{channel}/latest.json', feed)
            else:
                for row, item in prepared:
                    target = {'macos': 'darwin', 'windows': 'windows', 'linux': 'linux'}[row['platform']] + '-' + {'x86_64': 'amd64', 'arm64': 'arm64', 'universal': 'universal'}[row['arch']]
                    mutable(f'{self.prefix}/feeds/{channel}/update-{target}.json', item.native)
            info['channels'][channel] = release
        info['history'] = [h for h in info.get('history', []) if h['updateVersion'] != release['updateVersion']] + [release]
        info['history'] = sorted(info['history'], key=lambda r: (version(r['updateVersion']), r['buildSeq']))[-30:]
        mutable(f'{self.prefix}/release-info.json', info)
        record.update(status='published', releaseInfo=release)
        state['history'] = [h for h in state['history'] if h['updateVersion'] != release['updateVersion']] + [{**release, 'updates': updates}]
        state['history'] = sorted(state['history'], key=lambda r: (version(r['updateVersion']), r['buildSeq']))[-30:]
        self.save(state, etag)
        return release
