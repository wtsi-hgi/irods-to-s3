"""
Copyright (c) 2020 Genome Research Limited

Author: Christopher Harrison <ch12@sanger.ac.uk>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License along
with this program. If not, see https://www.gnu.org/licenses/
"""

from __future__ import annotations

import os
import re
import typing as T
from configparser import ConfigParser
from dataclasses import dataclass
from ipaddress import ip_address
from pathlib import Path

import boto3
from botocore.client import S3 as S3Client


_S3_URL = re.compile(r"""
    ^s3://
    (?P<bucket> (?!-)[a-z0-9-]+(?<!-)
                (\.(?!-)[a-z0-9-]+(?<!-))* )
    (?: / (?P<key> .*))?$
    """, re.VERBOSE | re.ASCII)

_S3_KEY_SPECIAL = re.compile(r"[&$@=;:+ ,?\x00-\x1f\x7f]")

_S3_KEY_AVOID = re.compile(r"[\^\"\\{}\[\]<>#~%`|\x80-\xff]")

def _is_ip(address:str) -> bool:
    to_test = int(address) if address.isdecimal() else address

    try:
        _ = ip_address(to_test)
    except ValueError:
        return False

    return True


class InvalidS3URL(Exception):
    """ Raised when an S3 URL cannot be parsed """

class InvalidS3Bucket(InvalidS3URL):
    """ Raised when an S3 bucket name is invalid """

class InvalidS3Config(Exception):
    """ Raised when no/invalid S3 configuration is found """


@dataclass(init=False)
class S3Object:
    bucket:str
    key:T.Optional[str]

    # Key characters contents
    has_special:bool
    has_restricted:bool

    def __init__(self, s3_url:str) -> None:
        match = _S3_URL.match(s3_url)
        if match is None:
            raise InvalidS3URL(f"Cannot parse S3 URL: {s3_url}")

        self.bucket = bucket = match["bucket"]
        self.key    = key    = match["key"] or None

        if not 2 < len(bucket) < 64:
            raise InvalidS3Bucket(f"S3 bucket name is too short/long: {bucket}")

        if _is_ip(bucket):
            raise InvalidS3Bucket(f"S3 bucket name must not be an IP address: {bucket}")

        self.has_special    = bool(_S3_KEY_SPECIAL.search(key or ""))
        self.has_restricted = bool(_S3_KEY_AVOID.search(key or ""))

    def __truediv__(self, path:T.Union[Path, str]) -> S3Object:
        # Syntactic sugar (similar to pathlib) for appending a path to
        # the S3 object (e.g., you can do: s3_obj / "path/to/somewhere")
        path = Path(path)
        if path.is_absolute():
            root = Path("/")
            path = path.relative_to(root)

        key = Path(self.key or "") / Path(path)
        return S3Object(f"s3://{self.bucket}/{key}")

    @property
    def url(self) -> str:
        # Construct and return the S3 URL
        key = self.key or ""
        return f"s3://{self.bucket}/{key}"


def client(config:T.Optional[Path] = None) -> S3Client:
    if config is None:
        # Get configuration from environment
        for env_var in "AWS_ACCESS_KEY_ID",\
                       "AWS_SECRET_ACCESS_KEY",\
                       "S3_ENDPOINT_URL":

            if not env_var in os.environ:
                raise InvalidS3Config(f"S3 environment variable not set: {env_var}")

        return boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT_URL"))

    # Otherwise, attempt to parse an s3cmd configuration file
    config = config.expanduser().resolve()
    if not config.exists():
        raise FileNotFoundError(f"No s3cmd configuration found in {config}")

    c = ConfigParser()
    c.read(config)

    if not c.has_section("default"):
        raise InvalidS3Config(f"Invalid s3cmd configuration; no \"default\" profile")

    for key in "host_base", "access_key", "secret_key":
        if not c.has_option("default", key):
            raise InvalidS3Config(f"Invalid s3cmd configuration; no \"{key}\" option")

    https = c.has_option("default", "use_https") and c.getboolean("default", "use_https")
    endpoint = ("https" if https else "http") + "://" + c.get("default", "host_base")

    return boto3.client("s3", use_ssl=https,
                              endpoint_url=endpoint,
                              aws_access_key_id=c.get("default", "access_key"),
                              aws_secret_access_key=c.get("default", "secret_key"))
