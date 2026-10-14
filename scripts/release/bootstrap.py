#!/usr/bin/env python3
"""Install checksum-pinned public binaries and native system prerequisites."""
import hashlib
import io
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tarfile
import tomllib
import urllib.request
import zipfile

from common import ReleaseError, run_cli

XCODEGEN_URL = 'https://github.com/yonaskolb/XcodeGen/releases/download/2.46.0/xcodegen.zip'
XCODEGEN_SHA256 = '4d9e34b62172d645eed6457cac13fc222569974098ef4ee9c3368bedf0196806'
MINISIGN = {
    'macos': ('minisign-0.12-macos.zip', '89000b19535765f9cffc65a65d64a820f433ef6db8020667f7570e06bf6aac63'),
    'linux': ('minisign-0.12-linux.tar.gz', '9a599b48ba6eb7b1e80f12f36b94ceca7c00b7a5173c95c3efc88d9822957e73'),
    'windows': ('minisign-0.12-win64.zip', '37b600344e20c19314b2e82813db2bfdcc408b77b876f7727889dbd46d539479'),
}


def run(args):
    subprocess.run(args, check=True)


def add_path(directory):
    with open(os.environ['GITHUB_PATH'], 'a', encoding='utf-8') as path:
        path.write(str(directory) + '\n')


def download(url, checksum):
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != checksum:
        raise ReleaseError('official public tool archive checksum mismatch')
    return data


def rust_toolchain():
    config = tomllib.loads(Path('.private-source/rust-toolchain.toml').read_text())['toolchain']
    channel = config['channel']
    targets = config.get('targets', [])
    if not isinstance(channel, str) or not re.fullmatch(r'\d+\.\d+\.\d+', channel):
        raise ReleaseError('Rust release toolchain must be exact')
    if not isinstance(targets, list) or any(not isinstance(t, str) or not re.fullmatch(r'[a-zA-Z0-9_-]+', t) for t in targets):
        raise ReleaseError('invalid Rust toolchain targets')
    if os.environ['PLATFORM'] == 'macos':
        apple_targets = {
            'arm64': ['aarch64-apple-darwin'],
            'x86_64': ['x86_64-apple-darwin'],
            'universal': ['aarch64-apple-darwin', 'x86_64-apple-darwin'],
        }
        targets = list(dict.fromkeys(targets + apple_targets[os.environ['ARCH']]))
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        output.write(f'channel={channel}\ntargets={",".join(targets)}\n')


def host_architecture():
    host = platform.machine().lower()
    architecture = {'amd64': ('x64', 'x86_64'), 'x86_64': ('x64', 'x86_64'),
                    'arm64': ('arm64', 'aarch64'), 'aarch64': ('arm64', 'aarch64')}.get(host)
    if architecture is None:
        raise ReleaseError('unsupported native runner host architecture')
    return architecture


def windows_fxc():
    sdk_arch, _ = host_architecture()
    kits = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Windows Kits/10/bin'
    candidates = sorted((p for p in kits.glob('10.*') if p.is_dir()), key=lambda p: tuple(map(int, p.name.split('.'))), reverse=True)
    fxc = next((p / sdk_arch / 'fxc.exe' for p in candidates if (p / sdk_arch / 'fxc.exe').is_file()), None)
    if fxc is None:
        raise ReleaseError('Windows SDK native fxc.exe not installed for runner host')
    result = subprocess.run([str(fxc), '/?'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise ReleaseError('Windows SDK fxc.exe is not executable on this runner')
    add_path(fxc.parent)


def minisign(native_platform):
    name, checksum = MINISIGN[native_platform]
    data = download('https://github.com/jedisct1/minisign/releases/download/0.12/' + name, checksum)
    directory = Path(os.environ['RUNNER_TEMP']) / 'agili-public-minisign'
    directory.mkdir(exist_ok=True)
    executable = directory / ('minisign.exe' if native_platform == 'windows' else 'minisign')
    if native_platform == 'linux':
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            member = archive.extractfile(f'minisign-linux/{host_architecture()[1]}/minisign')
            if member is None:
                raise ReleaseError('official Minisign binary missing')
            executable.write_bytes(member.read())
    else:
        member = f'minisign-win64/{host_architecture()[1]}/minisign.exe' if native_platform == 'windows' else 'minisign'
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            executable.write_bytes(archive.read(member))
    executable.chmod(0o755)
    result = subprocess.run([str(executable), '-v'], check=True, capture_output=True, text=True)
    if 'minisign 0.12' not in (result.stdout + result.stderr).lower():
        raise ReleaseError('official Minisign version mismatch')
    add_path(directory)


def main(native_platform):
    if native_platform == 'rust-toolchain':
        rust_toolchain()
        return
    if native_platform == 'macos':
        data = download(XCODEGEN_URL, XCODEGEN_SHA256)
        directory = Path(os.environ['RUNNER_TEMP']) / 'agili-public-xcodegen'
        # Keep the official bin/share layout so XcodeGen finds its presets.
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            archive.extractall(directory)
        executable = directory / 'xcodegen/bin/xcodegen'
        executable.chmod(0o755)
        if subprocess.check_output([str(executable), '--version'], text=True).strip() != 'Version: 2.46.0':
            raise ReleaseError('XcodeGen binary version mismatch')
        add_path(executable.parent)
    elif native_platform == 'linux':
        run(['sudo', 'apt-get', 'update'])
        run(['sudo', 'apt-get', 'install', '-y', 'build-essential', 'pkg-config', 'clang', 'libfreetype-dev', 'libwebp-dev', 'libvulkan-dev', 'cmake', 'libsodium-dev', 'libssl-dev', 'libfontconfig1-dev',
             'libxcb1-dev', 'libxkbcommon-dev', 'libxkbcommon-x11-dev', 'libwayland-dev', 'libegl1-mesa-dev'])
    elif native_platform == 'windows':
        windows_fxc()
    else:
        raise ReleaseError('unknown native platform')
    minisign(native_platform)


if __name__ == '__main__':
    run_cli(lambda: main(sys.argv[1]))
