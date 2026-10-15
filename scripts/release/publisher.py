#!/usr/bin/env python3
"""Release CLI; native source builders own packaging and signatures."""
import argparse
import base64
import json
import os
import re
import subprocess
from urllib.parse import quote, urlparse
import urllib.request

from builder import build_release
from common import PRODUCTS, ReleaseError, run_cli, targets
from releases import Publisher
from storage import R2


def github(path):
    request = urllib.request.Request('https://api.github.com/repos/' + path,
                                    headers={'Authorization': 'Bearer ' + os.environ['SOURCE_TOKEN'], 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['plan', 'build', 'publish', 'webhook', 'cleanup'])
    parser.add_argument('--product', required=True, choices=PRODUCTS)
    parser.add_argument('--run-id', default=os.environ.get('RELEASE_RUN_ID') or os.environ.get('GITHUB_RUN_ID'))
    parser.add_argument('--platform')
    parser.add_argument('--arch')
    args = parser.parse_args()
    if not args.run_id:
        parser.error('--run-id is required outside GitHub Actions')
    if not re.fullmatch(r'[1-9][0-9]*', args.run_id):
        parser.error('--run-id must be a positive integer string')
    if args.command != 'cleanup' and os.environ.get('GITHUB_RUN_ATTEMPT', '1') != '1':
        raise ReleaseError('workflow reruns are disabled; start a new workflow_dispatch release')
    if args.command == 'build' and (not args.platform or not args.arch):
        parser.error('--platform and --arch are required for build')
    publisher = Publisher(R2(), args.product, os.environ.get('DOWNLOAD_BASE_URL'))
    if args.command == 'plan':
        rebuild_input = os.environ.get('RELEASE_REBUILD', 'false')
        if rebuild_input not in {'true', 'false'}:
            raise ReleaseError('RELEASE_REBUILD must be true or false')
        rebuild = rebuild_input == 'true'
        state, _ = publisher.state()
        if str(args.run_id) in state['runs']:
            raise ReleaseError('run already reserved; start a new workflow_dispatch release')
        repo = PRODUCTS[args.product][0]
        sha = github(repo + '/commits/' + quote(os.environ.get('SOURCE_REF', 'main'), safe=''))['sha']
        if not re.fullmatch('[0-9a-f]{40}', sha):
            raise ReleaseError('source commit must be full SHA')
        doc = github(repo + '/contents/scripts/release/platforms.json?ref=' + sha)
        matrix = targets(json.loads(base64.b64decode(doc['content'])))
        record = publisher.reserve(args.run_id, os.environ['CHANNEL'], os.environ.get('VERSION', ''), os.environ.get('BUMP', 'patch'), sha, matrix, os.environ.get('SOURCE_REF', 'main'), rebuild)
        publisher.prune_stages(args.run_id)
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write('sha=' + record['sourceSha'] + '\nrepo=' + PRODUCTS[args.product][0] + '\nmatrix=' + json.dumps({'include': record['matrix']}) + '\n')
    elif args.command == 'cleanup':
        publisher.cleanup_run(args.run_id)
    elif args.command == 'build':
        build_release(publisher, args.run_id, args.platform, args.arch)
    elif args.command == 'publish':
        publisher.publish(args.run_id)
        print('Native release metadata completed.')
    else:
        record = publisher.reservation(args.run_id)
        if record['status'] != 'published':
            raise ReleaseError('webhook requires completed release')
        hook = os.environ.get('DEPLOY_WEBHOOK_URL', '')
        if not hook:
            print('Deployment webhook is empty; skipped.')
            return
        parsed = urlparse(hook)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.query or parsed.fragment or parsed.username or any(c.isspace() for c in hook):
            raise ReleaseError('webhook must be absolute HTTPS without query/fragment')
        subprocess.run(['curl', '-fsS', '-X', 'POST', hook], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    run_cli(main)
