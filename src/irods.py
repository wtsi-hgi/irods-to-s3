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

import os
import ssl
import typing as T
from collections import defaultdict
from pathlib import Path

from irods.data_object import iRODSDataObject
from irods.collection import iRODSCollection
from irods.session import iRODSSession


class NotAbsolute(Exception):
    """ Raised when the path to an iRODS object is not absolute """

class NoSuchObject(Exception):
    """ Raised when an iRODS object doesn't exist """

class CannotDescend(Exception):
    """ Raised when expanding a collection without recursion """


# iRODS Data Object or Collection
_iRODSObject = T.Union[iRODSDataObject, iRODSCollection]

def _is_collection(obj:_iRODSObject) -> bool:
    return isinstance(obj, iRODSCollection)


_irods_env = os.getenv("IRODS_ENVIRONMENT_FILE",
                       os.path.expanduser("~/.irods/irods_environment.json"))

_ssl = {"ssl_context": ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                                  cafile=None,
                                                  capath=None,
                                                  cadata=None)}
def session() -> iRODSSession:
    """
    Convenience wrapper to create an iRODS session with the usual
    environment configuration and a secure connection
    """
    return iRODSSession(irods_env_file=_irods_env, **_ssl)


def get_irods_object(session:iRODSSession, path:Path) -> _iRODSObject:
    """
    Get the appropriate iRODS object at the given path, if it exists

    @param   session  iRODS session
    @param   path     iRODS path to object
    @return  iRODS object (data object or collection)
    """
    if not path.is_absolute():
        raise NotAbsolute(f"iRODS path {path} must be absolute")

    path_s = str(path)

    if session.collections.exists(path_s):
        return session.collections.get(path_s)

    if session.data_objects.exists(path_s):
        return session.data_objects.get(path_s)

    raise NoSuchObject(f"iRODS object {path} doesn't exist")


def expand(*objs:_iRODSObject, recursive:bool = True) -> T.Iterator[iRODSDataObject]:
    """
    Generator of iRODS data objects, expanded recursively by default,
    from a list of sources

    @param   *objs      Objects to expand
    @param   recursive  Descend collections recursively
    @return  Iterator of data objects
    """
    for obj in objs:
        if _is_collection(obj):
            if not recursive:
                raise CannotDescend(f"iRODS object at {obj.path} is a collection")

            yield from obj.data_objects
            yield from expand(*obj.subcollections)

        else:
            yield obj


def metadata(obj:iRODSDataObject, *, key_delimiter:str = "; ", unit_delimiter:str = " ") -> T.Optional[T.Dict[str, str]]:
    avus = obj.metadata.items()

    if len(avus) == 0:
        return None

    collapsed = defaultdict(list)
    for avu in avus:
        value = avu.value
        if avu.unit:
            value = f"{value}{unit_delimiter}{avu.unit}"

        collapsed[avu.key].append(value)

    return {key: key_delimiter.join(value) for key, value in collapsed.items()}
