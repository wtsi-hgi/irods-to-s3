#!/usr/bin/env python

# Quick-and-Dirty iRODS-to-S3 copy
# Christopher Harrison <ch12@sanger.ac.uk>

import os
import ssl
import sys
from collections import deque
from urllib.parse import urlparse

import boto3
from botocore.errorfactory import ClientError
from irods.session import iRODSSession


_usage = f"Usage: {sys.argv[0]} [--force] IRODS_DATA_OBJECT s3://BUCKET[/S3_OBJECT]"
_ssl = {"ssl_context": ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)}


if __name__ == "__main__":
    argv = deque(sys.argv[1:])

    force = False
    if argv and argv[0] == "--force":
        force = True
        argv.popleft()

    try:
        irods_obj, s3_url = argv
    except ValueError:
        print("Invalid arguments!")
        print(_usage)
        sys.exit(1)

    irods_env = os.getenv("IRODS_ENVIRONMENT_FILE",
                          os.path.expanduser("~/.irods/irods_environment.json"))

    for env_var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_ENDPOINT_URL"]:
        if not env_var in os.environ:
            print(f"S3 environment variable not set: {env_var}")
            print(_usage)
            sys.exit(1)

    parsed_url = urlparse(s3_url)
    if parsed_url.scheme != "s3" or parsed_url.netloc == "":
        print("Invalid S3 URL")
        print(_usage)
        sys.exit(1)

    s3_bucket = parsed_url.netloc
    s3_obj = parsed_url.path

    with iRODSSession(irods_env_file=irods_env, **_ssl) as session:
        if not session.data_objects.exists(irods_obj):
            print(f"Data object not found on iRODS: {irods_obj}")
            print(_usage)
            sys.exit(1)

        data_object = session.data_objects.get(irods_obj)
        irods_checksum = data_object.checksum
        irods_size = data_object.size

        def _progress(so_far):
            print(f"Copied {so_far} of {irods_size} bytes; {so_far/irods_size:.1%} complete")

        if s3_obj in ("", "/"):
            s3_obj = data_object.path

        s3_url = f"s3://{s3_bucket}{s3_obj}"

        S3 = boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT_URL"))

        try:
            _ = S3.head_object(Bucket=s3_bucket, Key=s3_obj)

            if not force:
                print(f"File already exists on S3: {s3_url}")
                print(_usage)
                sys.exit(1)

            print("File exists on S3, deleting: {s3_url}")
            S3.delete_object(Bucket=s3_bucket, Key=s3_obj)

        except ClientError:
            # Object doesn't exist on S3, so carry on
            pass

        with data_object.open("rb") as irods_stream:
            S3.upload_fileobj(irods_stream, s3_bucket, s3_obj, callback=_progress)

        print("Upload complete")

        # S3 uses the ETag on an object for its checksum, which is an
        # MD5 sum when not a multipart upload. For a multipart upload, a
        # different algorithm is used. We therefore can't easily compare
        # the iRODS checksum with the S3 one :(
