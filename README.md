# iRODS to S3

A quick-and-dirty iRODS to S3 copy tool.

Usage:

    irods-to-s3.py [--force] IRODS_DATA_OBJECT s3://BUCKET[/S3_OBJECT]

Copy `IRODS_DATA_OBJECT` to the S3 `BUCKET`, either preserving the
iRODS's data object path, or to a specific location using `S3_OBJECT`.
The `--force` option can be supplied to overwrite the S3 object, if it
already exists.
