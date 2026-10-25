#!/usr/bin/env python3
"""Regenerate Homebrew and Scoop manifests from stable metadata on latest main."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from common import PRODUCTS, ReleaseError, run_cli, validate_minimum_system_version
from storage import R2
from sync_scoop import scoop_paths, update_scoop


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


def cask_paths(product):
    tokens = ('tinymd', 'tinymd-app', 'tinymd-cli') if product == 'tinymd' else (product,)
    return [f'Casks/{token}.rb' for token in tokens]


def update_cask(checkout, product, release):
    mac = [a for a in release['downloads'] if a['platform'] == 'macos' and a['format'] in {'dmg', 'zip'} and a.get('role', 'gui') == 'gui']
    universal = [a for a in mac if a['arch'] == 'universal']
    native = [next(a for a in mac if a['arch'] == arch) for arch in ('arm64', 'x86_64') if any(a['arch'] == arch for a in mac)]
    chosen = native if len(native) == 2 else universal[:1] or native
    if not chosen:
        raise ReleaseError('stable release has no macOS Cask installer')
    minimums = [a.get('minimumSystemVersion') for a in chosen]
    minimum = max(minimums, key=validate_minimum_system_version)
    for filename in cask_paths(product):
        render_cask(checkout / filename, product, release, chosen, minimum)


def asset_config(assets):
    if assets[0]['arch'] == 'universal':
        asset = assets[0]
        return f'  sha256 "{asset["sha256"]}"\n\n  url "{asset["url"]}"'
    return '\n'.join(
        f'  on_{"arm" if a["arch"] == "arm64" else "intel"} do\n'
        f'    sha256 "{a["sha256"]}"\n    url "{a["url"]}"\n  end'
        for a in assets
    )


def platform_block(platform, text):
    return f'  on_{platform} do\n' + '\n'.join('  ' + line if line else '' for line in text.splitlines()) + '\n  end'


def render_cask(path, product, release, chosen, minimum):
    token = path.stem
    linux_role = 'cli' if token == 'tinymd-cli' else 'gui'
    linux = [a for a in release['downloads']
             if a['platform'] == 'linux' and a['format'] == 'tar.gz'
             and a['arch'] in {'arm64', 'x86_64'} and a.get('role', 'gui') == linux_role]
    if token == 'tinymd':
        cli_arches = {a['arch'] for a in release['downloads']
                      if a['platform'] == 'linux' and a['format'] == 'tar.gz'
                      and a.get('role', 'gui') == 'cli' and a['arch'] in {'arm64', 'x86_64'}}
        linux = [a for a in linux if a['arch'] in cli_arches]
    linux = [next(a for a in linux if a['arch'] == arch)
             for arch in ('arm64', 'x86_64') if any(a['arch'] == arch for a in linux)]

    name, description, homepage = {
        'tinymd': ('TinyMD', 'A minimal Markdown editor', 'https://tinymd.app'),
        'tinymd-app': ('TinyMD', 'A minimal Markdown editor', 'https://tinymd.app'),
        'tinymd-cli': ('TinyMD CLI', 'A command-line tool for Markdown documents', 'https://tinymd.app'),
        'metrix-bar': ('Metrix.Bar', 'A minimal menu bar metrics monitor', 'https://metrix.bar'),
    }[token]
    requirement = macos_requirement(minimum)
    if chosen[0]['arch'] != 'universal' and len(chosen) == 1:
        requirement += f'\n  depends_on arch: :{chosen[0]["arch"]}'
    mac_conflict = {
        'tinymd': '  conflicts_with cask: "tinymd-cli"',
        'tinymd-cli': '  conflicts_with cask: "tinymd"',
    }.get(token, '')
    mac_artifacts = {
        'tinymd': '  app "TinyMD.app"\n  binary "#{appdir}/TinyMD.app/Contents/Helpers/tinymd"',
        'tinymd-app': '  app "TinyMD.app"',
        'tinymd-cli': '  binary "TinyMD.app/Contents/Helpers/tinymd"',
        'metrix-bar': '  app "Metrix.Bar.app"',
    }[token]
    if token != 'tinymd-cli':
        bundle = 'bar.metrix' if product == 'metrix-bar' else 'app.tinymd.TinyMD'
        mac_artifacts += (f'\n\n  zap trash: [\n'
                          f'    "~/Library/Application Support/{bundle}",\n'
                          f'    "~/Library/Caches/{bundle}",\n'
                          f'    "~/Library/Preferences/{bundle}.plist",\n'
                          f'    "~/Library/Saved Application State/{bundle}.savedState",\n  ]')
    metadata = f'  name "{name}"\n  desc "{description}"\n  homepage "{homepage}"'
    common = []
    if token != 'tinymd-cli':
        common.append('  auto_updates true')
    if token in {'tinymd', 'tinymd-app'}:
        common.append(f'  conflicts_with cask: "{"tinymd-app" if token == "tinymd" else "tinymd"}"')
    if linux:
        mac = '\n\n'.join(filter(None, [asset_config(chosen), requirement, mac_conflict, mac_artifacts]))
        linux_config = asset_config(linux)
        if len(linux) == 1:
            linux_config += f'\n\n  depends_on arch: :{linux[0]["arch"]}'
        if token == 'tinymd':
            linux_config += '\n\n  depends_on cask: "agili-app/tap/tinymd-cli"'
        linux_binary = {
            'tinymd': '  binary "TinyMD", target: "tinymd-app"',
            'tinymd-app': '  binary "TinyMD", target: "tinymd-app"',
            'tinymd-cli': '  binary "tinymd"',
            'metrix-bar': '  binary "metrix-bar"',
        }[token]
        body = '\n\n'.join(filter(None, [metadata, '\n'.join(common), platform_block('macos', mac),
                                               platform_block('linux', linux_config + '\n\n' + linux_binary)]))
    else:
        body = '\n\n'.join(filter(None, [asset_config(chosen), metadata,
                                               '\n'.join([requirement, *common, *([mac_conflict] if mac_conflict else [])]),
                                               mac_artifacts]))
    path.write_text(f'cask "{token}" do\n  version "{release["displayVersion"]}"\n\n{body}\nend\n')


def git(directory, *args, check=True):
    return subprocess.run(['git', '-C', str(directory), *args], check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def sync(product, stable_reader, remote='origin', branch='main', attempts=3):
    # An isolated checkout avoids resetting the workflow's scripts/private outputs.
    remote_url = git(Path.cwd(), 'remote', 'get-url', remote).stdout.strip()
    with tempfile.TemporaryDirectory(prefix='agili-packages-') as temporary:
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
            update_scoop(checkout, product, stable)
            filenames = cask_paths(product) + scoop_paths(product)
            git(checkout, 'add', *filenames)
            if git(checkout, 'diff', '--cached', '--quiet', '--', *filenames, check=False).returncode == 0:
                return 'unchanged'
            git(checkout, 'commit', '-m', f'chore(packages): sync stable {product} release')
            if git(checkout, 'push', 'origin', f'HEAD:refs/heads/{branch}', check=False).returncode == 0:
                return 'updated'
        raise ReleaseError('Package manifest push failed after bounded fetch/regenerate retries')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--product', required=True, choices=PRODUCTS)
    args = parser.parse_args()
    store = R2()
    prefix = PRODUCTS[args.product]['prefix']
    def stable():
        data, _ = store.get(f'{prefix}/release-info.json')
        return json.loads(data)['channels']['stable'] if data else None
    print('Package manifest sync: ' + sync(args.product, stable))


if __name__ == '__main__':
    run_cli(main)
