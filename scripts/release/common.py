"""Shared release constants, validation and safe CLI diagnostics."""
import hashlib
import json
import re
import sys

from semver import Version

PRODUCTS = {'tinymd': ('miantiao-me/TinyMD.app', 'tinymd-app'),
            'metrix-bar': ('miantiao-me/Metrix.Bar', 'metrix-bar')}
DYNAMIC = 'public, max-age=300, s-maxage=300, must-revalidate'
IMMUTABLE = 'public, max-age=31536000, immutable'
RUNNERS = {'macos': {'macos-latest', 'macos-15', 'macos-15-intel', 'macos-14'},
           'windows': {'windows-latest', 'windows-2025', 'windows-11-arm'},
           'linux': {'ubuntu-latest', 'ubuntu-24.04', 'ubuntu-24.04-arm'}}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


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


def validate_build_seq(seq):
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
