# iRODS to S3

Copy files from iRODS to S3.

## Usage

    irods-to-s3 [-h] [-f] [-R] [--make-bucket] [--ignore-avus] [-v]
                [--forbid-special | --allow-restricted] [--s3cfg S3CFG]
                SOURCE [SOURCE ...] s3://BUCKET[/KEY]

### Positional Arguments

    SOURCE              iRODS source data objects or collections
    s3://BUCKET[/KEY]   S3 destination

### Optional Arguments

    -f, --force         Overwrite files that exist at the destination
    -R, --recursive     Copy iRODS collections recursively
    --make-bucket       Make S3 bucket if it does not exist
    --ignore-avus       Don't replicate the iRODS AVUs on S3
    -v, --verbose       Verbose output

### S3 Key Character Control

    --forbid-special    Forbid S3 special characters in the destination keys
    --allow-restricted  Allow S3 restricted characters in the destination keys

Special characters are those that might require special handling in S3
keys:

* Ampersand ("&")
* Dollar ("$")
* ASCII character ranges 0x00–0x1F and 0x7F
* Commercial at symbol ("@")
* Equals ("=")
* Semicolon (";")
* Colon (":")
* Plus ("+")
* Space
* Comma (",")
* Question mark ("?")

Restricted characters are those that ought to be avoided in S3 keys:

* Backslash ("\\")
* Left curly brace ("{")
* Non-printable ASCII characters (0x80-0xFF)
* Caret ("^")
* Right curly brace ("}")
* Percent character ("%")
* Back tick ("`")
* Right square bracket ("]")
* Quotation marks
* Greater than symbol (">")
* Left square bracket ("[")
* Tilde ("~")
* Less than symbol ("<")
* Hash character ("#")
* Pipe symbol ("|")

### `s3cmd` Interaction

    --s3cfg S3CFG       Use s3cmd configuration, rather than from environment

By default, the S3 configuration will be taken from the environment
variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and
`S3_ENDPOINT_URL`. Alternatively, the `s3cmd` configuration in file
`S3CFG` can be used.
