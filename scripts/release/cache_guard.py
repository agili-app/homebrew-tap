#!/usr/bin/env python3
"""Only public dependency downloads enter shared caches; never compiler outputs."""
import os
from pathlib import Path
import sys
import tomllib

from common import ReleaseError, run_cli


def main(product):
    values = {}
    source = Path('.private-source')
    if product == 'metrix-bar':
        # No direct/private proxy fallback or credentialed Git fetch enters GOMODCACHE.
        for line in (source / 'go.sum').read_text().splitlines():
            module = line.split()[0]
            if any(prefix in module.lower() for prefix in ('miantiao-me/', 'agili-app/')):
                raise ReleaseError('private product dependency cannot enter public module cache')
        values = {'GOMODCACHE': str(Path(os.environ['RUNNER_TEMP']) / 'agili-public-gomod'),
                  'GOPROXY': 'https://proxy.golang.org', 'GOSUMDB': 'sum.golang.org',
                  'GOPRIVATE': '', 'GONOPROXY': '', 'GONOSUMDB': ''}
    else:
        lock = tomllib.loads((source / 'Cargo.lock').read_text())
        for package in lock['package']:
            origin = package.get('source', '')
            if origin.startswith('registry+') and origin != 'registry+https://github.com/rust-lang/crates.io-index':
                raise ReleaseError('only public crates.io registry enters shared cache')
        # Git deps deliberately stay uncached, as do target and Cargo credentials.
    with open(os.environ['GITHUB_ENV'], 'a') as env:
        for key, value in values.items():
            env.write(f'{key}={value}\n')


if __name__ == '__main__':
    run_cli(lambda: main(sys.argv[1]))
