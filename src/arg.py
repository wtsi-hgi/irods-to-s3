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

from argparse import ArgumentParser
from pathlib import Path

from .s3 import S3Object


arg_parser = ArgumentParser(description="Copy files from iRODS to S3")

arg_parser.add_argument("-f", "--force", action="store_true",
    help="overwrite files that exist at the destination")
arg_parser.add_argument("-R", "--recursive", action="store_true",
    help="copy iRODS collections recursively")
arg_parser.add_argument("--make-bucket", action="store_true",
    help="make S3 bucket if it does not exist")
arg_parser.add_argument("--ignore-avus", action="store_true",
    help="don't replicate the iRODS AVUs on S3")
arg_parser.add_argument("--dry-run", action="store_true",
    help="don't transfer any data, only log what will happen")
arg_parser.add_argument("-v", "--verbose", action="store_true",
    help="verbose output")

char_args = arg_parser.add_argument_group("S3 key character control")
char_args_mutex = char_args.add_mutually_exclusive_group()
char_args_mutex.add_argument("--forbid-special", action="store_true",
    help="forbid S3 special characters in the destination keys")
char_args_mutex.add_argument("--allow-restricted", action="store_true",
    help="allow S3 restricted characters in the destination keys")

s3cmd_args = arg_parser.add_argument_group("s3cmd interaction")
s3cmd_args.add_argument("--s3cfg",
    help="use s3cmd configuration, rather than from environment")

arg_parser.add_argument("source", metavar="SOURCE", type=Path, nargs="+",
    help="iRODS source data objects or collections")
arg_parser.add_argument("target", metavar="s3://BUCKET[/KEY]", type=S3Object,
    help="S3 destination")


parse = arg_parser.parse_args
help  = arg_parser.print_help
