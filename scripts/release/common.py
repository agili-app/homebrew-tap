"""Shared release constants, validation and safe CLI diagnostics."""
import hashlib
import json
import re
import sys
from urllib.parse import quote

from semver import Version

APPLE_CREDENTIALS = {
    'appleTeamId': 'APPLE_TEAM_ID',
    'notaryAppleId': 'NOTARY_APPLE_ID',
    'notaryPassword': 'NOTARY_APP_SPECIFIC_PASSWORD',
}
PRODUCTS = {
    'tinymd': {
        'repo': 'miantiao-me/TinyMD.app',
        'prefix': 'tinymd-app',
        'updater': 'gpui',
        'credentials': {
            **APPLE_CREDENTIALS,
            'updatePublicKey': 'TINYMD_UPDATE_PUBLIC_KEY',
            'updatePrivateKey': 'TINYMD_UPDATE_PRIVATE_KEY',
            'developerIdP12Base64': 'TINYMD_DEVELOPER_ID_P12_BASE64',
            'developerIdP12Password': 'TINYMD_DEVELOPER_ID_P12_PASSWORD',
            'signingIdentity': 'TINYMD_SIGNING_IDENTITY',
            'profileApp': 'PROVISIONING_PROFILE_APP_BASE64',
            'profilePreview': 'PROVISIONING_PROFILE_PREVIEW_BASE64',
            'deployWebhookUrl': 'TINYMD_DEPLOY_WEBHOOK_URL',
        },
    },
    'metrix-bar': {
        'repo': 'miantiao-me/Metrix.Bar',
        'prefix': 'metrix-bar',
        'updater': 'mygo',
        'credentials': {
            **APPLE_CREDENTIALS,
            'updatePublicKey': 'METRIX_UPDATE_PUBLIC_KEY',
            'updatePrivateKey': 'METRIX_UPDATE_PRIVATE_KEY',
            'developerIdP12Base64': 'METRIX_DEVELOPER_ID_P12_BASE64',
            'developerIdP12Password': 'METRIX_DEVELOPER_ID_P12_PASSWORD',
            'signingIdentity': 'METRIX_SIGNING_IDENTITY',
            'profileApp': '',
            'profilePreview': '',
            'deployWebhookUrl': 'METRIX_DEPLOY_WEBHOOK_URL',
        },
    },
}
DYNAMIC = 'public, max-age=300, s-maxage=300, must-revalidate'
IMMUTABLE = 'public, max-age=31536000, immutable'
RUNNERS = {'macos': {'macos-latest', 'macos-26', 'macos-15', 'macos-15-intel', 'macos-14'},
           'windows': {'windows-latest', 'windows-2025', 'windows-11-arm'},
           'linux': {'ubuntu-latest', 'ubuntu-24.04', 'ubuntu-24.04-arm'}}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def public_artifact_url(base, relative_path, product_prefix=None):
    """Resolve an object key with a product-root base; two-argument calls stay relative."""
    if product_prefix is not None:
        if base.rsplit('/', 1)[-1] != product_prefix:
            raise ReleaseError('public download base must end with product prefix')
        if relative_path.startswith(('stable/' + product_prefix + '/', 'preview/' + product_prefix + '/')):
            base = base.rsplit('/', 1)[0]
        else:
            relative_path = relative_path.removeprefix(product_prefix + '/')
    return base + '/' + quote(relative_path, safe='/')


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ReleaseError(Exception):
    """A diagnostic generated locally and safe to display in CI."""


def run_cli(main):
    try:
        main()
    except ReleaseError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print('Release step failed (' + type(exc).__name__ + ').', file=sys.stderr)
        sys.exit(1)


def version(value):
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-preview\.(0|[1-9]\d*))?', value):
        raise ReleaseError('invalid release version')
    return Version.parse(value)


def updater_protocol(product):
    protocol = PRODUCTS[product]['updater']
    if protocol not in {'gpui', 'mygo'}:
        raise ReleaseError('unsupported updater protocol')
    return protocol


def validate_build_seq(seq):
    if type(seq) is not int:
        raise ReleaseError('buildSeq must be an integer')
    if not 0 < seq <= 9999 * 10000:
        raise ReleaseError('buildSeq exceeds Apple version capacity')


def validate_minimum_system_version(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d+(?:\.\d+){0,2}', value):
        raise ReleaseError('invalid or missing macOS minimumSystemVersion')
    return tuple(int(n) for n in value.split('.'))


def targets(document):
    if document.get('schemaVersion') != 1:
        raise ReleaseError('unsupported platform schema')
    rows = document['targets']
    if not rows:
        raise ReleaseError('source owner has enabled no verified targets')
    seen = set()
    for row in rows:
        key = (row['platform'], row['arch'])
        if key in seen or row['platform'] not in RUNNERS or row['arch'] not in {'arm64', 'x86_64', 'universal'}:
            raise ReleaseError('invalid/duplicate platform target')
        if row['arch'] == 'universal' and row['platform'] != 'macos':
            raise ReleaseError('universal only supported on macOS')
        if row['runner'] not in RUNNERS[row['platform']]:
            raise ReleaseError('unsupported runner')
        seen.add(key)
    return rows
