#!/usr/bin/env python3
"""Regenerate one Cask from current stable metadata on the latest main branch."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

from common import PRODUCTS, ReleaseError, run_cli, validate_minimum_system_version
from storage import R2


# Homebrew's MacOSVersion::SYMBOLS; publishing runs on Linux without Homebrew.
MACOS_RELEASES = {
    11: 'big_sur',
    12: 'monterey',
    13: 'ventura',
    14: 'sonoma',
    15: 'sequoia',
    26: 'tahoe',
    27: 'golden_gate',
}


def macos_requirement(minimum):
    version = validate_minimum_system_version(minimum)
    major = version[0]
    symbol = MACOS_RELEASES.get(major)
    if symbol is None:
        raise ReleaseError(f'unsupported Homebrew macOS minimum {minimum}; update MACOS_RELEASES from Homebrew MacOSVersion::SYMBOLS')
    requirement = f'  depends_on macos: :{symbol}'
    if any(version[1:]):
        requirement = (f'  # macOS {minimum} required; Homebrew allows {major}.0+, but macOS <{minimum} is rejected by LSMinimumSystemVersion on launch.\n'
                       + requirement)
    return requirement


def update_cask(checkout, product, release):
    mac = [a for a in release['downloads'] if a['platform'] == 'macos' and a['format'] in {'dmg', 'zip'} and a.get('role', 'gui') == 'gui']
    universal = [a for a in mac if a['arch'] == 'universal']
    chosen = universal[:1] or [next(a for a in mac if a['arch'] == arch) for arch in ('arm64', 'x86_64') if any(a['arch'] == arch for a in mac)]
    if not chosen:
        raise ReleaseError('stable release has no macOS Cask installer')
    minimums = [a.get('minimumSystemVersion') for a in chosen]
    minimum = max(minimums, key=validate_minimum_system_version)
    path = checkout / 'Casks' / (product + '.rb')
    text = path.read_text()
    text = re.sub(r'^  version ".*"', f'  version "{release["displayVersion"]}"', text, flags=re.M)
    homepage = {'tinymd': 'https://tinymd.app', 'metrix-bar': 'https://metrix.bar'}[product]
    text = re.sub(r'^  homepage ".*"', f'  homepage "{homepage}"', text, flags=re.M)
    start = text.index('\n', text.index('  version ')) + 1
    end = text.index('  name ', start)
    if universal:
        asset = chosen[0]
        replacement = f'  sha256 "{asset["sha256"]}"\n\n  url "{asset["url"]}"\n'
    else:
        replacement = '\n' + '\n'.join(f'  on_{"arm" if a["arch"] == "arm64" else "intel"} do\n    sha256 "{a["sha256"]}"\n    url "{a["url"]}"\n  end' for a in chosen) + '\n'
    text = text[:start] + replacement + text[end:]
    text = re.sub(r'^  depends_on arch: .*\n', '', text, flags=re.M)
    if not universal and len(chosen) == 1:
        text = text.replace('  auto_updates true', f'  depends_on arch: :{chosen[0]["arch"]}\n  auto_updates true')
    text = re.sub(r'^  # macOS .*?required;.*?\n(?=  depends_on macos:)', '', text, flags=re.M | re.S)
    text = re.sub(r'^  # macOS .*?LSMinimumSystemVersion on launch\.\n', '', text, flags=re.M | re.S)
    requirement = macos_requirement(minimum)
    if re.search(r'^  depends_on macos:', text, flags=re.M):
        text = re.sub(r'^  depends_on macos:.*', requirement, text, flags=re.M)
    else:
        text = text.replace('  auto_updates true', requirement + '\n  auto_updates true')
    path.write_text(text)


def git(directory, *args, check=True):
    return subprocess.run(['git', '-C', str(directory), *args], check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def sync(product, stable_reader, remote='origin', branch='main', attempts=3):
    # An isolated checkout avoids resetting the workflow's scripts/private outputs.
    remote_url = git(Path.cwd(), 'remote', 'get-url', remote).stdout.strip()
    with tempfile.TemporaryDirectory(prefix='agili-cask-') as temporary:
        checkout = Path(temporary)
        git(checkout, 'init')
        git(checkout, 'remote', 'add', 'origin', remote_url)
        # Resolve checkout's includeIf credentials before forwarding to the isolated checkout.
        auth = git(Path.cwd(), 'config', '--includes', '--get-regexp', r'^http\..*\.extraheader$', check=False)
        for line in auth.stdout.splitlines():
            key, value = line.split(' ', 1)
            git(checkout, 'config', key, value)
        git(checkout, 'config', 'user.name', 'Agili')
        git(checkout, 'config', 'user.email', 'git@agili.app')
        for _ in range(attempts):
            git(checkout, 'fetch', 'origin', branch)
            git(checkout, 'checkout', '-B', 'cask-sync', 'FETCH_HEAD')
            stable = stable_reader()
            if stable is None:
                raise ReleaseError('stable metadata missing')
            update_cask(checkout, product, stable)
            filename = f'Casks/{product}.rb'
            if git(checkout, 'diff', '--quiet', '--', filename, check=False).returncode == 0:
                return 'unchanged'
            git(checkout, 'add', filename)
            git(checkout, 'commit', '-m', f'chore(casks): sync stable {product} release')
            if git(checkout, 'push', 'origin', f'HEAD:refs/heads/{branch}', check=False).returncode == 0:
                return 'updated'
        raise ReleaseError('Cask push failed after bounded fetch/regenerate retries')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--product', required=True, choices=PRODUCTS)
    args = parser.parse_args()
    store = R2()
    prefix = PRODUCTS[args.product][1]
    def stable():
        data, _ = store.get(f'{prefix}/release-info.json')
        return json.loads(data)['channels']['stable'] if data else None
    print('Cask sync: ' + sync(args.product, stable))


if __name__ == '__main__':
    run_cli(main)
