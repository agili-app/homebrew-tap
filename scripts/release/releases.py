"""Reservation, baseline selection and one-shot release publication."""
import json
import re
from datetime import datetime, timezone
from email.message import Message

from artifacts import prepare_target
from common import PRODUCTS, DYNAMIC, IMMUTABLE, ReleaseError, digest, encoded, public_artifact_url, updater_protocol, version, validate_build_seq


class Publisher:
    def __init__(self, store, product, base=None):
        self.store = store
        self.product = product
        self.prefix = PRODUCTS[product]['prefix']
        self.updater = updater_protocol(product)
        self.base = (base or f'https://downloads.agili.app/{self.prefix}').rstrip('/')
        if not self.base.startswith('https://'):
            raise ReleaseError('public download base must be HTTPS')
        public_artifact_url(self.base, '', self.prefix)
        self.control = f'{self.prefix}/control.json'

    def state(self):
        data, etag = self.store.get(self.control, True)
        state = json.loads(data) if data else {'seq': 0, 'runs': {}, 'history': []}
        self.watermarks(state)
        return state, etag

    def watermarks(self, state):
        if max(state.get('previews', {}).values(), default=0) > state['seq']:
            raise ReleaseError('legacy preview counter exceeds buildSeq')
        records = list(state['runs'].values()) + state['history']
        def maximum(field, values):
            state[field] = max([state.get(field, '0.0.0')] + values, key=version)
        maximum('highestDisplayVersion', [r['displayVersion'] for r in records])
        maximum('highestStableVersion', [r['displayVersion'] for r in records if r['channel'] == 'stable'])
        published = [r['displayVersion'] for r in state['runs'].values()
                     if r['channel'] == 'stable' and r['status'] == 'published']
        published += [r['displayVersion'] for r in state['history'] if r['channel'] == 'stable']
        stable = state.get('channels', {}).get('stable')
        maximum('publishedStableVersion', published)
        # Channel ownership is reserved before publication completes: freeze it, but do not mark it published.
        frozen = [str(version(stable['updateVersion']))] if stable else []
        maximum('highestStableVersion', [state['publishedStableVersion']] + frozen)
        maximum('highestDisplayVersion', [state['highestStableVersion']])
        state['lastRunId'] = max([int(state.get('lastRunId', 0))] + [int(run) for run in state['runs']])
        state.pop('previews', None)

    def save(self, state, etag):
        self.watermarks(state)
        state['runs'] = dict(sorted(state['runs'].items(), key=lambda item: item[1]['buildSeq'], reverse=True)[:3])
        state['history'] = sorted(state['history'], key=lambda r: (version(r['updateVersion']), r['buildSeq']))[-3:]
        self.store.put(self.control, encoded(state), True, etag=etag, absent=etag is None)

    def reservation(self, run):
        state, _ = self.state()
        return state['runs'][str(run)]

    def reserve(self, run, channel, requested, bump, sha, matrix, source_ref='main', rebuild=False):
        if not isinstance(rebuild, bool):
            raise ReleaseError('rebuild must be a boolean')
        if rebuild and channel != 'stable':
            raise ReleaseError('rebuild requires stable channel')
        state, etag = self.state()
        run = str(run)
        if run in state['runs']:
            raise ReleaseError('run already reserved; start a new workflow_dispatch release')
        if not re.fullmatch(r'[1-9][0-9]*', run):
            raise ReleaseError('runId must be a positive integer')
        if int(run) <= state['lastRunId']:
            raise ReleaseError('outside retained reservation window')
        highest = state['highestDisplayVersion']
        base = requested
        if not base:
            base = str(getattr(version(highest), 'bump_' + bump)())
        if version(base).prerelease is not None:
            raise ReleaseError('display version must be X.Y.Z')
        frozen = state['highestStableVersion']
        if rebuild:
            if not requested or state['publishedStableVersion'] == '0.0.0' or version(base) != version(state['publishedStableVersion']):
                raise ReleaseError('rebuild requires the current published stable version explicitly')
        elif channel == 'stable':
            if version(base) < version(frozen) or version(base) <= version(state['publishedStableVersion']):
                raise ReleaseError('stable version is frozen; published versions require rebuild')
        elif version(base) <= version(frozen) and not (requested == base == frozen):
            raise ReleaseError('preview version is frozen; request the current base explicitly')
        state['seq'] += 1
        validate_build_seq(state['seq'])
        update = base if channel == 'stable' else f'{base}-preview.{state["seq"]}'
        record = {'runId': run, 'product': self.product, 'channel': channel,
                  'sourceSha': sha, 'sourceRef': source_ref, 'displayVersion': base, 'updateVersion': update,
                  'buildSeq': state['seq'], 'artifactPrefix': f'{channel}/{self.prefix}/releases', 'matrix': matrix, 'status': 'reserved',
                  'requestedVersion': requested, 'bump': bump, 'rebuild': rebuild,
                  'publishedAt': datetime.now(timezone.utc).isoformat()}
        if channel == 'stable':
            record['artifactPath'] = f'{update}/build-{record["buildSeq"]}'
        state['runs'][run] = record
        self.save(state, etag)
        return record

    def prune_stages(self, run):
        self.store.prune_stages(f'{self.prefix}/runs/', str(run))

    def cleanup_run(self, run):
        self.store.delete_prefix(f'{self.prefix}/runs/{run}/')

    def stage_key(self, run, platform, arch):
        return f'{self.prefix}/runs/{run}/{platform}-{arch}.zip'

    def stage(self, run, platform, arch, data):
        key = self.stage_key(run, platform, arch)
        self.store.put(key, data, True, absent=True)

    def immutable(self, key, data):
        if '\r' in key or '\n' in key:
            raise ReleaseError('invalid attachment filename')
        filename = re.sub(r'[^A-Za-z0-9._-]', '_', key.rsplit('/', 1)[-1]) or 'download'
        header = Message()
        header.add_header('Content-Disposition', 'attachment', filename=filename)
        old, _ = self.store.get(key)
        if old is not None:
            raise ReleaseError('immutable artifact collision')
        self.store.put(key, data, absent=True, cache=IMMUTABLE,
                       disposition=header['Content-Disposition'])
        self.store.verify_public(public_artifact_url(self.base, key, self.prefix), data)

    def baseline(self, run, platform, arch, directory):
        state, _ = self.state()
        record = state['runs'][str(run)]
        current = version(record['updateVersion'])
        history = sorted(state['history'], key=lambda r: (version(r['updateVersion']), r['buildSeq']), reverse=True)
        result, counts = [], {}
        for previous in history:
            if previous['channel'] != record['channel'] or version(previous['updateVersion']) >= current:
                continue
            for item in previous['updates']:
                format = item['format']
                if (item['platform'], item['arch']) != (platform, arch) or counts.get(format, 0) >= 3:
                    continue
                data, _ = self.store.get(item['key'])
                if data is None and record['channel'] == 'preview':
                    continue
                if data is None or digest(data) != item['sha256']:
                    raise ReleaseError('baseline missing or digest mismatch')
                path = directory / (previous['updateVersion'] + '-' + item['name'])
                baseline = {**{k: item[k] for k in ('platform', 'arch', 'format', 'sha256', 'url')},
                            'updateVersion': previous['updateVersion'], 'path': str(path.resolve())}
                if item.get('signatureKey'):
                    signature, _ = self.store.get(item['signatureKey'])
                    if signature is None and record['channel'] == 'preview':
                        continue
                    if signature is None or digest(signature) != item['signatureSha256']:
                        raise ReleaseError('baseline signature missing or digest mismatch')
                    signature_path = directory / (path.name + '.minisig')
                    signature_path.write_bytes(signature)
                    baseline['signaturePath'] = str(signature_path.resolve())
                if item.get('nativeManifest'):
                    baseline['nativeManifest'] = item['nativeManifest']
                path.write_bytes(data)
                counts[format] = counts.get(format, 0) + 1
                result.append(baseline)
        return result

    def prepare(self, record, row, bundle):
        return prepare_target(self.product, self.prefix, self.base, record, row, bundle)

    def can_advance(self, record, current):
        if not current:
            return True
        if record['buildSeq'] <= current['buildSeq']:
            return False
        if version(record['updateVersion']) >= version(current['updateVersion']):
            return True
        # An explicit same-base preview may follow the stable package shared into its feed.
        return (record['channel'] == 'preview'
                and record.get('requestedVersion') == record['displayVersion']
                and version(current['updateVersion']).prerelease is None
                and current['updateVersion'] == record['displayVersion'])

    def publish(self, run):
        state, etag = self.state()
        record = state['runs'][str(run)]
        if record['status'] != 'reserved':
            raise ReleaseError('run cannot be published again; start a new workflow_dispatch release')
        record['status'] = 'publishing'
        self.save(state, etag)
        state, etag = self.state()
        record = state['runs'][str(run)]
        public_data, _ = self.store.get(f'{self.prefix}/release-info.json')
        info = json.loads(public_data) if public_data else {'schemaVersion': 1, 'product': self.product, 'channels': {'stable': None, 'preview': None}, 'history': []}
        highwaters = state.setdefault('channels', {})
        for channel, live in info['channels'].items():
            if live and channel not in highwaters:
                highwaters[channel] = {'runId': None, 'updateVersion': live['updateVersion'], 'buildSeq': live['buildSeq']}
        channel = record['channel']
        if not all(self.can_advance(record, current) for current in (
                info['channels'].get(channel), highwaters.get(channel))):
            raise ReleaseError('superseded reservation cannot advance mutable release metadata')
        channels = [channel]
        if channel == 'stable' and all(self.can_advance(record, current) for current in (
                info['channels'].get('preview'), highwaters.get('preview'))):
            channels.append('preview')
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
        release = {k: record[k] for k in ('displayVersion', 'updateVersion', 'channel', 'buildSeq', 'publishedAt')}
        release.update(notes=record.get('notes', ''), downloads=downloads)
        for channel in channels:
            highwaters[channel] = {'runId': str(run), 'updateVersion': record['updateVersion'], 'buildSeq': record['buildSeq']}
        # Freeze all selected channels before the first mutable PUT, even if a later PUT fails.
        self.save(state, etag)
        state, etag = self.state()
        record = state['runs'][str(run)]
        if self.updater == 'gpui':
            feed = {'schema_version': 1, 'version': record['updateVersion'], 'buildSeq': record['buildSeq'],
                    'notes': release['notes'], 'assets': [a for _, item in prepared for a in item.assets]}
            payload = encoded(feed)
            for channel in channels:
                self.store.put(f'{self.prefix}/feeds/{channel}/latest.json', payload, cache=DYNAMIC)
        elif self.updater == 'mygo':
            for row, item in prepared:
                target = {'macos': 'darwin', 'windows': 'windows', 'linux': 'linux'}[row['platform']] + '-' + {'x86_64': 'amd64', 'arm64': 'arm64', 'universal': 'universal'}[row['arch']]
                payload = encoded(item.native)
                for channel in channels:
                    self.store.put(f'{self.prefix}/feeds/{channel}/update-{target}.json', payload, cache=DYNAMIC)
        for channel in channels:
            info['channels'][channel] = release
        info['history'] = [h for h in info.get('history', []) if h['updateVersion'] != release['updateVersion']] + [release]
        info['history'] = sorted(info['history'], key=lambda r: (version(r['updateVersion']), r['buildSeq']))[-3:]
        self.store.put(f'{self.prefix}/release-info.json', encoded(info), cache=DYNAMIC)
        record.update(status='published', releaseInfo=release)
        state['history'] = [h for h in state['history'] if h['updateVersion'] != release['updateVersion']] + [{**release, 'updates': updates}]
        state['history'] = sorted(state['history'], key=lambda r: (version(r['updateVersion']), r['buildSeq']))[-3:]
        self.save(state, etag)
        return release
