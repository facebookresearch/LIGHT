#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


from abc import ABC, abstractmethod
from omegaconf import MISSING, DictConfig
from contextlib import contextmanager

from typing import Optional, Union, Dict, Any


class BaseDB(ABC):
    """
    Core database class underneath the LIGHT datamodel that allows for
    linking to production MySQL on RDS when live, and SQLite when testing
    or using LIGHT locally. Also abstracts away file reading and writing,
    which can be done with either buckets or local file manipulation.

    Output conversions of production dbs to local copies done
    currently with: https://github.com/dumblob/mysql2sqlite
    """

    def __init__(self, config: "DictConfig"):
        """
        Create this database, either connecting to a remote host or local
        files and instances.
        """

    @abstractmethod
    def _complete_init(self, config: "DictConfig"):
        """
        Complete implementation-specific initialization
        """
        raise NotImplementedError()

    @abstractmethod
    def _validate_init(self):
        """
        Ensure that this database is initialized correctly
        """
        raise NotImplementedError()

    def write_data_to_file(
        self, data: Union[str, Dict[str, Any]], filename: str, json_encode: bool = False
    ):
        """
        Write the given data to the provided filename
        in the correct storage location (local or remote)
        """
        # Expects data to be a string, unless json_encode is True

    def read_data_from_file(self, filename: str, json_encoded: bool = False):
        """
        Read the data from the given filename from wherever it
        is currently stored (local or remote)
        """

    def open_file(self):
        try:
            file = open(self.file_name, "w")
            yield file
        finally:
            file.close()

    @contextmanager
    def get_database_connection(self):
        """Get a connection to the database that can be used for a transaction"""
        try:
            # Get DB connection
            # yield db connection
            raise NotImplementedError()
        finally:
            # close DB connection, rollback if there's an issue
            pass
