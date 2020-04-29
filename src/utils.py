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

import typing as T
from math import ceil, log10


_SI  = ["", "k",  "M",  "G",  "T",  "P"]
_IEC = ["", "Ki", "Mi", "Gi", "Ti", "Pi"]

def human_size(value:float, base:int = 1024, threshold:float = 0.8) -> str:
    """ Quick-and-dirty size quantifier """
    quantifiers = _IEC if base == 1024 else _SI
    sigfigs = ceil(log10(base * threshold))

    order = 0
    while order < len(quantifiers) - 1 and value > base * threshold:
        value /= base
        order += 1

    return f"{value:.{sigfigs}g} {quantifiers[order]}"


def hex2bytes(hex_string:T.Optional[str]) -> T.Optional[bytes]:
    return bytes.fromhex(hex_string or "") or None
