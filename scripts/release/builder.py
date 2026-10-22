"""Build private native sources, redact diagnostics and stage signed packages for this run."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from artifacts import bundle_directory
from common import ReleaseError


def build_release(publisher, run, platform, arch):
    record = publisher.reservation(run)
    if record['status'] != 'reserved':
        raise ReleaseError('build requires a fresh reserved run')
    if not any((row['platform'], row['arch']) == (platform, arch) for row in record['matrix']):
        raise ReleaseError('target does not match reservation')
    source = Path('.private-source').resolve()
    if subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() != record['sourceSha']:
        raise ReleaseError('source checkout SHA mismatch')
    workspace = Path('.release-output').resolve()
    workspace.mkdir(exist_ok=True)
    packages = workspace / 'packages'
    packages.mkdir(exist_ok=True)
    if any(packages.iterdir()):
        raise ReleaseError('package output must be empty before a fresh build')
    baselines = workspace / 'baselines'
    baselines.mkdir(exist_ok=True)
    env = {name: value for name, value in os.environ.items()
           if not name.startswith('R2_') and name not in {
               'SOURCE_TOKEN', 'GH_TOKEN', 'GITHUB_TOKEN', 'DEVELOPER_ID_P12_BASE64',
               'DEVELOPER_ID_P12_PASSWORD', 'NOTARY_APPLE_ID', 'NOTARY_APP_SPECIFIC_PASSWORD',
               'PROVISIONING_PROFILE_APP_BASE64', 'PROVISIONING_PROFILE_PREVIEW_BASE64',
           }}
    other_keys = ('MYGO_UPDATER_PRIVATE_KEY', 'METRIX_UPDATE_PUBLIC_KEY') if publisher.product == 'tinymd' else (
        'TINYMD_UPDATE_PRIVATE_KEY', 'TINYMD_UPDATE_PRIVATE_KEY_PATH', 'TINYMD_UPDATE_PUBLIC_KEY')
    for name in other_keys:
        env.pop(name, None)
    env['RELEASE_BASELINES_JSON'] = json.dumps(publisher.baseline(run, platform, arch, baselines))
    env['CARGO_TARGET_DIR'] = str(workspace / 'target')
    env['GOCACHE'] = str(workspace / 'gocache')
    if env.get('APPLE_TEAM_ID'):
        env['DEVELOPMENT_TEAM'] = env.get('DEVELOPMENT_TEAM') or env['APPLE_TEAM_ID']
    key_path = None
    try:
        if publisher.product == 'tinymd':
            secret = env.pop('TINYMD_UPDATE_PRIVATE_KEY', '')
            if secret:
                with tempfile.NamedTemporaryFile(prefix='agili-tinymd-key-', delete=False, mode='w') as key:
                    key_path = Path(key.name)
                    key_path.chmod(0o600)
                    key.write(secret)
                env['TINYMD_UPDATE_PRIVATE_KEY_PATH'] = str(key_path)
            elif not env.get('TINYMD_UPDATE_PRIVATE_KEY_PATH') or not Path(env['TINYMD_UPDATE_PRIVATE_KEY_PATH']).is_file():
                raise ReleaseError('TinyMD native private key is required')
        command = [sys.executable, str(source / 'scripts/release/build.py'), '--platform', platform, '--arch', arch,
                   '--update-version', record['updateVersion'], '--display-version', record['displayVersion'],
                   '--build-seq', str(record['buildSeq']), '--channel', record['channel'], '--output-dir', str(packages)]
        with (workspace / 'private-build.log').open('wb') as log:
            result = subprocess.run(command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            diagnostic = (workspace / 'private-build.log').read_bytes()
            # Include the original secret after removing it from the builder environment.
            sensitive = dict(os.environ, **env)
            for name, value in sensitive.items():
                if value and any(token in name for token in ('KEY', 'TOKEN', 'PASSWORD', 'SECRET', 'BASE64')):
                    diagnostic = diagnostic.replace(value.encode(), b'[REDACTED]')
            log_key = f'debug/{publisher.prefix}/{run}/{platform}-{arch}/private-build.log'
            publisher.store.put(log_key, diagnostic, True)
            print('Build exited ' + str(result.returncode) + '; private diagnostic: ' + log_key)
            raise ReleaseError('private source build failed')
        bundle = bundle_directory(packages)
        publisher.prepare(record, {'platform': platform, 'arch': arch}, bundle)
        publisher.stage(run, platform, arch, bundle)
    finally:
        if key_path is not None:
            key_path.unlink(missing_ok=True)
