"""Prepare isolated Certum tools and sign Windows release files before packaging."""
import argparse
import hashlib
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
import zipfile


SSIGN_VERSION = '0.1.11'
SSIGN_BASE = f'https://github.com/Le-Syl21/ssign/releases/download/v{SSIGN_VERSION}'
TOOLS = {
    'ssign.zip': (f'{SSIGN_BASE}/ssign-windows-x86_64.zip',
                  '3dacba75082d2949bae332f6dfac342843a85838db75deba9721b40b43fe73f0'),
    'pkcs11.zip': (f'{SSIGN_BASE}/ssign-pkcs11-windows-x86_64.zip',
                   '2c9704d6d07dc279bb1d693f45b3a3c5e1a432c6bc3650c374a12ee3c87a41d6'),
    'jsign.jar': ('https://github.com/ebourg/jsign/releases/download/7.6/jsign-7.6.jar',
                  '6cf58aa080e7ff82656f320cff8d4a3bff30408df8766806dcba3740dd839fa5'),
    'jre.zip': ('https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.21%2B9/OpenJDK17U-jre_x64_windows_hotspot_17.0.21_9.zip',
                'fe4656bd78fb09812dc38c49da777f79cc33e7ee435a254be82f9e7f40d9d117'),
}
TIMESTAMP_URL = 'http://time.certum.pl/'


def github_env(name, value):
    with Path(os.environ['GITHUB_ENV']).open('a', encoding='utf-8') as output:
        output.write(f'{name}={value}\n')


def prepare():
    root = Path(tempfile.mkdtemp(prefix='release-windows-signing-', dir=os.environ['RUNNER_TEMP']))
    # Export before downloads so always() cleanup also handles a partial preparation.
    github_env('RELEASE_WINDOWS_SIGNING_DIR', root)
    for name, (url, expected) in TOOLS.items():
        archive = root / name
        with urlopen(Request(url, headers={'User-Agent': 'agili-release'}), timeout=180) as response, archive.open('wb') as output:
            shutil.copyfileobj(response, output)
        with archive.open('rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() != expected:
                raise RuntimeError(f'Windows signing tool checksum mismatch: {name}')
        if name.endswith('.zip'):
            destination = root / name.removesuffix('.zip')
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(destination)
            archive.unlink()
    module = next((root / 'pkcs11').rglob('ssign_pkcs11.dll'))
    # x64 Java and PKCS#11 run together, including on ARM64 via Windows emulation.
    (root / 'pkcs11.cfg').write_text(
        f'name = CertumSimplySign\nlibrary = "{module.as_posix()}"\nslotListIndex = 0\n', encoding='utf-8')
    github_env('RELEASE_WINDOWS_SIGNER', Path(__file__).resolve())


def signing_root():
    root = os.environ.get('RELEASE_WINDOWS_SIGNING_DIR', '')
    if not root or not Path(root).is_dir():
        raise RuntimeError('Windows signing tools have not been prepared')
    return Path(root)


def signing_env(root):
    for name in ('CERTUM_EMAIL', 'CERTUM_OTP'):
        if not os.environ.get(name, '').strip():
            raise RuntimeError(f'Windows release signing requires {name}')
    session = root / 'runtime'
    session.mkdir(exist_ok=True)
    # Both ssign frontends share this private per-job cache; never upload/cache it.
    return dict(os.environ, XDG_RUNTIME_DIR=str(session))


def otp_period():
    seed = os.environ.get('CERTUM_OTP', '')
    if seed.startswith('otpauth://'):
        return int(parse_qs(urlparse(seed).query).get('period', ['30'])[0])
    return 30


def cloud_sign(command, env):
    for attempt in range(4):
        result = subprocess.run(command, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if not result.returncode:
            return
        # Only retry a rejected login. A failed signature/timestamp must stop packaging.
        if 'no authorization code after login' not in result.stdout + result.stderr or attempt == 3:
            # Provider output may include account/session data; keep it out of diagnostics.
            raise RuntimeError(f'Certum signing failed (exit {result.returncode})')
        period = otp_period()
        time.sleep(period - time.time() % period + random.uniform(1, 5))


def signtool():
    configured = shutil.which('signtool.exe')
    if configured:
        return configured
    kits = Path(os.environ['ProgramFiles(x86)']) / 'Windows Kits/10/bin'
    tools = sorted(kits.glob('10.*/x64/signtool.exe'), key=lambda p: tuple(map(int, p.parents[1].name.split('.'))))
    if not tools:
        raise RuntimeError('Windows SDK signtool.exe is required')
    return str(tools[-1])


def verify(paths):
    tool = signtool()
    for path in paths:
        # /tw makes a missing timestamp return a warning exit status, also rejected here.
        result = subprocess.run([tool, 'verify', '/pa', '/all', '/tw', str(path)], capture_output=True)
        if result.returncode:
            raise RuntimeError(f'Windows signature/timestamp verification failed: {path.name}')


def sign(paths):
    root = signing_root()
    env = signing_env(root)
    pe, packages = [], []
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f'Windows signing input is missing: {path.name}')
        if path.suffix.lower() in {'.exe', '.dll'}:
            pe.append(path)
        elif path.suffix.lower() == '.msix':
            packages.append(path)
        else:
            raise RuntimeError(f'Unsupported Windows signing format: {path.suffix}')
    if pe:
        executable = next((root / 'ssign').rglob('ssign.exe'))
        cloud_sign([str(executable), '--timestamp-url', TIMESTAMP_URL, *map(str, pe)], env)
    if packages:
        java = next((root / 'jre').rglob('java.exe'))
        for path in packages:
            cloud_sign([str(java), '-jar', str(root / 'jsign.jar'), '--storetype', 'PKCS11',
                        '--keystore', str(root / 'pkcs11.cfg'), '--storepass', 'NONE',
                        '--alias', 'Certum SimplySign (ssign)', '--alg', 'SHA-256',
                        '--tsaurl', TIMESTAMP_URL, '--tsmode', 'RFC3161', str(path)], env)
    verify(paths)
    print('Verified Windows signatures: ' + ', '.join(path.name for path in paths))


def subject(path):
    # Publisher must use the certificate's exact X.500 subject, including attribute order.
    script = "[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false); $s = Get-AuthenticodeSignature -LiteralPath $env:RELEASE_SIGNING_REFERENCE; if ($s.Status -ne 'Valid' -or !$s.SignerCertificate) { throw 'Invalid signed publisher reference' }; $s.SignerCertificate.Subject"
    result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                            env=dict(os.environ, RELEASE_SIGNING_REFERENCE=str(path)), check=True, capture_output=True)
    return result.stdout.decode('utf-8-sig').strip()


def cleanup():
    root = os.environ.get('RELEASE_WINDOWS_SIGNING_DIR')
    if root:
        path = Path(root).resolve()
        runner_temp = Path(os.environ['RUNNER_TEMP']).resolve()
        if path.parent != runner_temp or not path.name.startswith('release-windows-signing-'):
            raise RuntimeError('Refusing to remove a directory outside signing tools')
        shutil.rmtree(path)


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('prepare')
    commands.add_parser('cleanup')
    for name in ('sign', 'verify'):
        command = commands.add_parser(name)
        command.add_argument('paths', type=Path, nargs='+')
    publisher = commands.add_parser('subject')
    publisher.add_argument('path', type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare()
    elif args.command == 'cleanup':
        cleanup()
    elif args.command == 'subject':
        sys.stdout.buffer.write((subject(args.path) + '\n').encode('utf-8'))
    elif args.command == 'sign':
        sign(args.paths)
    else:
        verify(args.paths)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
