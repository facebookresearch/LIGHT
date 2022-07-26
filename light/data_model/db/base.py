#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


from abc import ABC, abstractmethod
from omegaconf import MISSING, DictConfig
from sqlalchemy import create_engine
from enum import Enum
from typing import Optional, Union, Dict, Any, Type
from uuid import uuid4
from dataclasses import dataclass
from tempfile import mkdtemp
import shutil
import os
import json

from hydra.core.config_store import ConfigStore

DEFAULT_LOG_PATH = "".join(
    [os.path.abspath(os.path.dirname(__file__)), "/../../../logs"]
)


@dataclass
class LightDBConfig:
    backend: str = "test"
    file_root: Optional[str] = DEFAULT_LOG_PATH


cs = ConfigStore.instance()
cs.store(name="config1", node=LightDBConfig)


class DBStatus(Enum):
    """Current review status for contents"""

    REVIEW = "unreviewed"
    PRODUCTION = "production"
    REJECTED = "rejected"
    QUESTIONABLE = "questionable"
    ACCEPTED = "accepted"


class DBSplitType(Enum):
    """Splits in the LIGHT Environment DB"""

    UNSET = "no_split_set"
    TRAIN = "train"
    TEST = "test"
    VALID = "valid"
    UNSEEN = "unseen_test"


class HasDBIDMixin:
    """Simple mixin for classes that define their own DBID schema"""

    ID_PREFIX: str  # ID prefix should be 3 characters max.

    @classmethod
    def get_id(cls: Type["HasDBIDMixin"]) -> str:
        """Create an ID for this class"""
        return f"{cls.ID_PREFIX}-{uuid4()}"

    @classmethod
    def is_id(cls: Type["HasDBIDMixin"], test_id: str) -> bool:
        """Check if a given ID refers to this class"""
        return test_id.startswith(f"{cls.ID_PREFIX}-")


class BaseDB(ABC):
    """
    Core database class underneath the LIGHT datamodel that allows for
    linking to production MySQL on RDS when live, and SQLite when testing
    or using LIGHT locally. Also abstracts away file reading and writing,
    which can be done with either buckets or local file manipulation.

    Output conversions of production dbs to local copies done
    currently with: https://github.com/dumblob/mysql2sqlite
    """

    DB_TYPE: str

    def __init__(self, config: "DictConfig"):
        """
        Create this database, either connecting to a remote host or local
        files and instances.
        """
        # TODO replace with a swappable engine that persists the data
        self.backend = config.backend
        if config.backend == "test":
            self.engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
            self.made_temp_dir = config.file_root is None
            if self.made_temp_dir:
                self.file_root = mkdtemp()
            else:
                self.file_root = config.file_root
        elif config.backend == "local":
            self.file_root = config.file_root
            db_path = os.path.join(self.file_root, f"{self.DB_TYPE}.db")
            self.engine = create_engine(f"sqlite:////{db_path}")
        else:
            raise NotImplementedError(
                f"Provided backend {config.backend} doens't exist"
            )
        self._complete_init(config)

    @abstractmethod
    def _complete_init(self, config: "DictConfig"):
        """
        Complete implementation-specific initialization
        """

    @abstractmethod
    def _validate_init(self):
        """
        Ensure that this database is initialized correctly
        """

    def _enforce_get_first(self, session, stmt, error_text) -> Any:
        """
        Enforce getting the first element using stmt, raise a key_error
        with error_text if fails to find
        """
        result = session.scalars(stmt).first()
        if result is None:
            raise KeyError(error_text)
        return result

    def file_path_exists(self, file_path: str) -> bool:
        """
        Determine if the given file path exists on this storage
        """
        if self.backend in ["test", "local"]:
            full_path = os.path.join(self.file_root, file_path)
            return os.path.exists(full_path)
        else:
            raise NotImplementedError

    def write_data_to_file(
        self, data: Union[str, Dict[str, Any]], filename: str, json_encode: bool = False
    ) -> None:
        """
        Write the given data to the provided filename
        in the correct storage location (local or remote)
        """
        if self.backend in ["test", "local"]:
            full_path = os.path.join(self.file_root, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w+") as target_file:
                if json_encode:
                    json.dump(data, target_file)
                else:
                    target_file.write(data)
        else:
            raise NotImplementedError()

    def read_data_from_file(
        self, filename: str, json_encoded: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        Read the data from the given filename from wherever it
        is currently stored (local or remote)
        """
        if self.backend in ["test", "local"]:
            full_path = os.path.join(self.file_root, filename)
            with open(full_path, "r") as target_file:
                if json_encoded:
                    return json.load(target_file)
                else:
                    return target_file.read()
        else:
            raise NotImplementedError()

    def open_file(self):
        try:
            file = open(self.file_name, "w")
            yield file
        finally:
            file.close()

    def shutdown(self):
        if self.backend == "test":
            if self.made_temp_dir:
                shutil.rmtree(self.file_root)
