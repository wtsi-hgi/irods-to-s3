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

import logging
import sys
import typing as T
from enum import Enum
from traceback import print_tb
from types import TracebackType


def _exception_handler(logger:logging.Logger) -> T.Callable:
    # Create an exception handler that logs uncaught exceptions (except
    # keyboard interrupts) and spews the traceback to stderr (in
    # debugging mode) before terminating
    def _log_uncaught_exception(exc_type:T.Type[Exception], exc_val:Exception, traceback:TracebackType) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_val, traceback)

        else:
            logger.critical(str(exc_val) or exc_type.__name__)
            if __debug__:
                print_tb(traceback)

            sys.exit(1)

    return _log_uncaught_exception


class Level(Enum):
    """ Convenience enumeration for logging levels """
    Debug    = logging.DEBUG
    Info     = logging.INFO
    Warning  = logging.WARNING
    Error    = logging.ERROR
    Critical = logging.CRITICAL


_ISO8601 = "%Y-%m-%dT%H:%M:%SZ%z"
_formatter = logging.Formatter(fmt="%(asctime)s\t%(levelname)s\t%(message)s", datefmt=_ISO8601)

class Logger:
    _logger:logging.Logger
    _level:Level

    def __init__(self, level:Level, formatter:logging.Formatter = _formatter) -> None:
        self._logger = logging.getLogger("is3")

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

        self.level = level

        sys.excepthook = _exception_handler(self._logger)

    def __call__(self, message:str, level:Level = Level.Info) -> None:
        """ Log a message at an optional level """
        self._logger.log(level.value, message)

    @property
    def level(self) -> Level:
        return self._level

    @level.setter
    def level(self, level:Level) -> None:
        self._level = level.value
        self._logger.setLevel(level.value)
        for handler in self._logger.handlers:
            handler.setLevel(level.value)

    def debug(self, message:str) -> None:
        # Convenience alias
        self(message, Level.Debug)

    def info(self, message:str) -> None:
        # Convenience alias
        self(message, Level.Info)

    def warning(self, message:str) -> None:
        # Convenience alias
        self(message, Level.Warning)

    def error(self, message:str) -> None:
        # Convenience alias
        self(message, Level.Error)

    def critical(self, message:str) -> None:
        # Convenience alias
        self(message, Level.Critical)
