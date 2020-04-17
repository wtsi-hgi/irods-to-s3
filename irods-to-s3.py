#!/usr/bin/env python

# Quick-and-Dirty iRODS-to-S3 copy, with verification
# Christopher Harrison <ch12@sanger.ac.uk>

import os
import ssl
import sys

from irods.session import iRODSSession


_usage = f"Usage: {sys.argv[0]} IRODS_DATA_OBJECT S3_URL"
_ssl = {"ssl_context": ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)}


if __name__ == "__main__":
    try:
        irods_obj, s3_url = sys.argv[1:]
    except ValueError:
        print("Invalid arguments!")
        print(_usage)
        sys.exit(1)

    irods_env = os.getenv("IRODS_ENVIRONMENT_FILE",
                          os.path.expanduser("~/.irods/irods_environment.json"))

    with iRODSSession(irods_env_file=irods_env, **_ssl) as session:
        pass
