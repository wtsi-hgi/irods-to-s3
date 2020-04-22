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

import re
import typing as T
from dataclasses import dataclass
from ipaddress import ip_address


_S3_URL = re.compile(r"""
    ^s3://
    (?P<bucket> (?!-)[a-z0-9-]+(?<!-)
                (\.(?!-)[a-z0-9-]+(?<!-))* )
    (?: / (?P<key> .*))?$
    """, re.VERBOSE | re.ASCII)

_S3_KEY_SPECIAL = re.compile(r"[&$@=;:+ ,?\x00-\x1f]")

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
