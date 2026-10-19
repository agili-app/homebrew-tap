#!/usr/bin/env python3
"""Render Scoop manifests from the same stable metadata used by Homebrew."""
import json

from common import ReleaseError


def scoop_paths(product):
    tokens = ('tinymd', 'tinymd-app', 'tinymd-cli') if product == 'tinymd' else (product,)
    return [f'bucket/{token}.json' for token in tokens]


def update_scoop(checkout, product, release):
    windows = [a for a in release['downloads']
               if a['platform'] == 'windows' and a['format'] == 'exe'
               and a['arch'] in {'arm64', 'x86_64'}]
    assets = {
        role: {arch: next(a for a in windows if a['arch'] == arch and a.get('role', 'gui') == role)
               for arch in ('arm64', 'x86_64')
               if any(a['arch'] == arch and a.get('role', 'gui') == role for a in windows)}
        for role in ('gui', 'cli')
    }
    rendered = {}
    for filename in scoop_paths(product):
        token = filename.rsplit('/', 1)[1].removesuffix('.json')
        role = 'cli' if token == 'tinymd-cli' else 'gui'
        arches = [arch for arch in ('arm64', 'x86_64') if arch in assets[role]
                  and (token != 'tinymd' or arch in assets['cli'])]
        if not arches:
            raise ReleaseError(f'stable release has no Windows Scoop assets for {token}')
        description, homepage = {
            'tinymd': ('A minimal Markdown editor', 'https://tinymd.app'),
            'tinymd-app': ('A minimal Markdown editor', 'https://tinymd.app'),
            'tinymd-cli': ('A command-line tool for Markdown documents', 'https://tinymd.app'),
            'metrix-bar': ('A minimal menu bar metrics monitor', 'https://metrix.bar'),
        }[token]
        architecture = {}
        for arch in arches:
            asset = assets[role][arch]
            target = 'tinymd-cli.exe' if role == 'cli' else 'TinyMD.exe'
            # Scoop selects 7-Zip by URL suffix; Metrix.Bar's NSIS payload is extractable.
            suffix = 'dl.7z' if product == 'metrix-bar' else target
            config = {'url': asset['url'] + '#/' + suffix, 'hash': asset['sha256']}
            if token == 'tinymd':
                cli = assets['cli'][arch]
                config = {'url': [config['url'], cli['url'] + '#/tinymd-cli.exe'],
                          'hash': [asset['sha256'], cli['sha256']]}
            architecture['arm64' if arch == 'arm64' else '64bit'] = config
        manifest = {
            'version': f'{release["displayVersion"]}.{release["buildSeq"]}',
            'description': description,
            'homepage': homepage,
            'license': 'Proprietary',
            'architecture': architecture,
            'bin': {
                'tinymd': [['tinymd-cli.exe', 'tinymd'], ['TinyMD.exe', 'tinymd-app']],
                'tinymd-app': [['TinyMD.exe', 'tinymd-app']],
                'tinymd-cli': [['tinymd-cli.exe', 'tinymd']],
                'metrix-bar': [['Metrix.Bar.exe', 'metrix-bar']],
            }[token],
        }
        if token != 'tinymd-cli':
            executable, name = ('Metrix.Bar.exe', 'Metrix.Bar') if product == 'metrix-bar' else ('TinyMD.exe', 'TinyMD')
            manifest['shortcuts'] = [[executable, name]]
        rendered[filename] = json.dumps(manifest, indent=4) + '\n'
    # Validate every variant before writing so missing GUI/CLI assets leave no partial set.
    for filename, content in rendered.items():
        path = checkout / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
