"""Private CAS storage and public object I/O."""
import mimetypes
import os
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
