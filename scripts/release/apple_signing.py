#!/usr/bin/env python3
"""Ephemeral Apple credentials for native builders; never print key material."""
import base64
import json
import shutil
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile


def quiet(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def prepare(product):
    required = ['DEVELOPER_ID_P12_BASE64', 'DEVELOPER_ID_P12_PASSWORD', 'MACOS_SIGNING_IDENTITY',
                'APPLE_TEAM_ID', 'NOTARY_APPLE_ID', 'NOTARY_APP_SPECIFIC_PASSWORD']
    if product == 'tinymd':
        required += ['PROVISIONING_PROFILE_APP_BASE64', 'PROVISIONING_PROFILE_PREVIEW_BASE64']
    if any(not os.environ.get(name) for name in required):
        raise ValueError('missing Apple signing credentials')
    root = Path(os.environ['RUNNER_TEMP']) / 'agili-apple-signing'
    root.mkdir(mode=0o700, exist_ok=True)
    keychain = root / 'release.keychain-db'
    profile = 'agili-release-notary'
    password = secrets.token_urlsafe(32)
    p12 = root / 'certificate.p12'
    p12.write_bytes(base64.b64decode(os.environ['DEVELOPER_ID_P12_BASE64'], validate=True))
    p12.chmod(0o600)
    search_list = subprocess.check_output(['security', 'list-keychains', '-d', 'user'], text=True)
    original = [line.strip().strip('"') for line in search_list.splitlines()]
    (root / 'search-list.json').write_text(json.dumps(original))
    quiet(['security', 'create-keychain', '-p', password, str(keychain)])
    quiet(['security', 'set-keychain-settings', '-lut', '21600', str(keychain)])
    quiet(['security', 'unlock-keychain', '-p', password, str(keychain)])
    quiet(['security', 'import', str(p12), '-k', str(keychain), '-P', os.environ['DEVELOPER_ID_P12_PASSWORD'],
           '-T', '/usr/bin/codesign', '-T', '/usr/bin/security'])
    p12.unlink()
    quiet(['security', 'set-key-partition-list', '-S', 'apple-tool:,apple:', '-s', '-k', password, str(keychain)])
    quiet(['security', 'list-keychains', '-d', 'user', '-s', str(keychain), *original])
    quiet(['xcrun', 'notarytool', 'store-credentials', profile, '--apple-id', os.environ['NOTARY_APPLE_ID'],
           '--team-id', os.environ['APPLE_TEAM_ID'], '--password', os.environ['NOTARY_APP_SPECIFIC_PASSWORD'],
           '--keychain', str(keychain)])
    installed = []
    if product == 'tinymd':
        destination = Path.home() / 'Library/MobileDevice/Provisioning Profiles'
        destination.mkdir(parents=True, exist_ok=True)
        for label in ('APP', 'PREVIEW'):
            data = base64.b64decode(os.environ[f'PROVISIONING_PROFILE_{label}_BASE64'], validate=True)
            path = destination / f'agili-{os.environ["GITHUB_RUN_ID"]}-{label}.provisionprofile'
            if path.exists():
                raise ValueError('profile path already exists')
            path.write_bytes(data)
            path.chmod(0o600)
            installed.append(str(path))
            (root / 'profiles.json').write_text(json.dumps(installed))
    with open(os.environ['GITHUB_ENV'], 'a') as env:
        env.write(f'MACOS_NOTARY_KEYCHAIN_PROFILE={profile}\nMACOS_NOTARY_KEYCHAIN={keychain}\nSIGNING_KEYCHAIN_NAME={keychain}\n')


def cleanup():
    root = Path(os.environ['RUNNER_TEMP']) / 'agili-apple-signing'
    if not root.exists():
        return
    errors = []
    def attempt(label, action):
        try:
            action()
        except Exception as exc:
            errors.append(label + ':' + type(exc).__name__)
    if (root / 'search-list.json').exists():
        attempt('restore-search-list', lambda: quiet(['security', 'list-keychains', '-d', 'user', '-s', *json.loads((root / 'search-list.json').read_text())]))
    keychain = root / 'release.keychain-db'
    if keychain.exists():
        attempt('delete-keychain', lambda: quiet(['security', 'delete-keychain', str(keychain)]))
    if (root / 'profiles.json').exists():
        profiles = []
        attempt('read-profiles', lambda: profiles.extend(json.loads((root / 'profiles.json').read_text())))
        for path in profiles:
            attempt('delete-profile', lambda path=path: Path(path).unlink(missing_ok=True))
    attempt('remove-temp-files', lambda: shutil.rmtree(root))
    if errors:
        raise RuntimeError('Apple cleanup failures: ' + ', '.join(errors))


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'cleanup':
            cleanup()
        else:
            prepare(sys.argv[2])
    except Exception as exc:
        print(str(exc) if sys.argv[1] == 'cleanup' else 'Apple credential step failed (' + type(exc).__name__ + ').', file=sys.stderr)
        sys.exit(1)
