"""Private CAS storage and public object I/O."""
import mimetypes
import os
import re
import urllib.request

import boto3
from botocore.exceptions import ClientError

from common import ReleaseError, digest


class R2:
    def __init__(self):
        self.public = os.environ['R2_PUBLIC_BUCKET']
        self.private = os.environ['R2_PRIVATE_BUCKET']
        if self.public == self.private:
            raise ReleaseError('private control bucket must be separate')
        self.client = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'], region_name='auto')

    def get(self, key, private=False):
        try:
            obj = self.client.get_object(Bucket=self.private if private else self.public, Key=key)
            return obj['Body'].read(), obj['ETag']
        except ClientError as exc:
            if exc.response['Error']['Code'] in {'NoSuchKey', '404'}:
                return None, None
            raise

    def put(self, key, data, private=False, etag=None, absent=False, cache=None, disposition=None):
        args = dict(Bucket=self.private if private else self.public, Key=key, Body=data,
                    ContentType=mimetypes.guess_type(key)[0] or 'application/octet-stream',
                    Metadata={'sha256': digest(data)})
        if etag:
            args['IfMatch'] = etag
        if absent:
            args['IfNoneMatch'] = '*'
        if cache:
            args['CacheControl'] = cache
        if disposition:
            args['ContentDisposition'] = disposition
        self.client.put_object(**args)

    def verify_public(self, url, data):
        request = urllib.request.Request(url, headers={'User-Agent': 'AgiliRelease/1.0'})
        with urllib.request.urlopen(request, timeout=120) as response:
            if response.status != 200 or digest(response.read()) != digest(data):
                raise ReleaseError('public artifact verification failed')

    def _stage_prefix(self, prefix):
        if prefix not in {'tinymd-app/runs/', 'metrix-bar/runs/'}:
            raise ReleaseError('invalid private stage prefix')
        return prefix

    def _delete_keys(self, keys):
        for offset in range(0, len(keys), 1000):
            response = self.client.delete_objects(
                Bucket=self.private, Delete={'Objects': [{'Key': key} for key in keys[offset:offset + 1000]], 'Quiet': True})
            if response.get('Errors'):
                raise ReleaseError('private stage deletion failed')

    def prune_stages(self, prefix, current_run, published_runs, cutoff):
        self._stage_prefix(prefix)
        published_runs = {str(run) for run in published_runs}
        for page in self.client.get_paginator('list_objects_v2').paginate(Bucket=self.private, Prefix=prefix):
            keys = []
            for obj in page.get('Contents', []):
                key = obj['Key']
                if not key.startswith(prefix):
                    continue
                match = re.fullmatch(r'([1-9][0-9]*)/.+', key[len(prefix):])
                if not match or match[1] == str(current_run):
                    continue
                if match[1] in published_runs or obj['LastModified'] < cutoff:
                    keys.append(key)
            self._delete_keys(keys)

    def delete_prefix(self, prefix):
        root, run, tail = prefix.rsplit('/', 2)
        self._stage_prefix(root + '/')
        if not re.fullmatch(r'[1-9][0-9]*', run) or tail:
            raise ReleaseError('invalid private run prefix')
        for page in self.client.get_paginator('list_objects_v2').paginate(Bucket=self.private, Prefix=prefix):
            self._delete_keys([obj['Key'] for obj in page.get('Contents', []) if obj['Key'].startswith(prefix)])
