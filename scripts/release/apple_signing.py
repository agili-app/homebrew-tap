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


_SECRET_VALUES = set()


def redact(text):
    values = _SECRET_VALUES | {
        value for name, value in os.environ.items()
        if value and any(marker in name.upper() for marker in
                         ('PASSWORD', 'SECRET', 'TOKEN', 'BASE64', 'APPLE_ID', 'ACCESS_KEY'))
    }
    for value in sorted(values, key=len, reverse=True):
        text = text.replace(value, '[REDACTED]')
    return text


def quiet(args):
    result = subprocess.run(args, capture_output=True, text=True, errors='replace')
    if result.returncode:
        program = Path(args[0]).name
        # Only fixed, known subcommands are safe; never render the argv.
        safe = {'security': {'create-keychain', 'set-keychain-settings', 'unlock-keychain',
                             'import', 'set-key-partition-list', 'list-keychains', 'delete-keychain'},
                'xcrun': {'notarytool'}}
        command = program if program in safe else 'Apple tool'
        if program in safe and len(args) > 1 and args[1] in safe[program]:
            command += ' ' + args[1]
            if args[1] == 'notarytool' and len(args) > 2 and args[2] == 'store-credentials':
                command += ' store-credentials'
        print(f'Apple command failed: {command}; exitcode={result.returncode}; stderr={redact(result.stderr).strip()}',
              file=sys.stderr)
        raise RuntimeError('Apple command failed')
    return result.stdout


def prepare():
    required = ['DEVELOPER_ID_P12_BASE64', 'DEVELOPER_ID_P12_PASSWORD', 'MACOS_SIGNING_IDENTITY',
                'APPLE_TEAM_ID', 'NOTARY_APPLE_ID', 'NOTARY_APP_SPECIFIC_PASSWORD']
    if any(not os.environ.get(name) for name in required):
        raise ValueError('missing Apple signing credentials')
    root = Path(os.environ['RUNNER_TEMP']) / 'agili-apple-signing'
    root.mkdir(mode=0o700, exist_ok=True)
    keychain = root / 'release.keychain-db'
    profile = 'agili-release-notary'
    password = secrets.token_urlsafe(32)
    _SECRET_VALUES.add(password)
    p12 = root / 'certificate.p12'
    p12.write_bytes(base64.b64decode(os.environ['DEVELOPER_ID_P12_BASE64'], validate=True))
    p12.chmod(0o600)
    search_list = quiet(['security', 'list-keychains', '-d', 'user'])
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
    attempt('remove-temp-files', lambda: shutil.rmtree(root))
    if errors:
        raise RuntimeError('Apple cleanup failures: ' + ', '.join(errors))


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'cleanup':
            cleanup()
        elif sys.argv[1] == 'prepare':
            prepare()
        else:
            raise ValueError('expected prepare or cleanup')
    except Exception as exc:
        print(str(exc) if sys.argv[1] == 'cleanup' else 'Apple credential step failed (' + type(exc).__name__ + ').', file=sys.stderr)
        sys.exit(1)
