#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from abc import ABC, abstractmethod
from omegaconf import MISSING, DictConfig  # type: ignore
from sqlalchemy import create_engine  # type: ignore
from enum import Enum
from typing import Optional, Union, Dict, Any, Type
from uuid import uuid4
from dataclasses import dataclass
from tempfile import mkdtemp
import shutil
import os
import json

from hydra.core.config_store import ConfigStore  # type: ignore

DEFAULT_LOG_PATH = "".join(
    [os.path.abspath(os.path.dirname(__file__)), "/../../../logs"]
)


@dataclass
class LightDBConfig:
    backend: str = "test"
    file_root: Optional[str] = None


@dataclass
class LightLocalDBConfig(LightDBConfig):
    backend: str = "local"
    file_root: Optional[str] = DEFAULT_LOG_PATH


@dataclass
class LightAWSDBConfig(LightDBConfig):
    backend: str = "aws-postgres"
    file_root: str = MISSING
    db_address: str = MISSING
    db_user: str = MISSING
    db_pass: str = MISSING


ALL_DB_CONFIGS_LIST = [
    LightDBConfig,
    LightLocalDBConfig,
    LightAWSDBConfig,
]


class DBStatus(Enum):
    """Current review status for contents"""

    REVIEW = "unreviewed"
    PRODUCTION = "production"
    REJECTED = "rejected"
    QUESTIONABLE = "questionable"  # For low quality, or borderline content
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

    def __init__(self, config: "LightDBConfig"):
        """
        Create this database, either connecting to a remote host or local
        files and instances.
        """
        self.backend = config.backend
        if config.backend == "test":
            self.engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
            self.made_temp_dir = config.file_root is None
            if self.made_temp_dir:
                self.file_root = mkdtemp()
            else:
                assert config.file_root is not None  # to make typing happy
                self.file_root = config.file_root
        elif config.backend == "local":
            assert config.file_root is not None, "Must provide valid file_root"
            self.file_root = config.file_root
            db_path = os.path.join(self.file_root, f"{self.DB_TYPE}.db")
            self.engine = create_engine(f"sqlite:////{db_path}")
        elif config.backend == "aws-postgres":
            try:
                import psycopg2  # type: ignore
                import boto3  # type: ignore
            except ImportError:
                print(
                    "For aws-postgres usage, you must also `pip install mysqlclient boto3 psycopg2-binary"
                )
                raise
            # Get DB registered and functioning
            assert isinstance(
                config, LightAWSDBConfig
            ), "Must use LightAWSDBConfig for aws-postgres"
            self.db_address = config.db_address
            db_address = config.db_address
            login_user = config.db_user
            login_pass = config.db_pass
            self.engine = create_engine(
                f"postgresql://{login_user}:{login_pass}@{db_address}:5432/postgres"
            )

            # Connect to the s3 filestore
            assert (
                config.file_root is not None
            ), "Must provide fileroot as s3 bucket address"
            self.file_root = config.file_root  # file root is a s3 bucket address
            s3 = boto3.resource("s3")
            self.bucket = s3.Bucket(self.file_root)  # type: ignore
        else:
            raise NotImplementedError(
                f"Provided backend {config.backend} doens't exist"
            )
        self._complete_init(config)

    @abstractmethod
    def _complete_init(self, config: "LightDBConfig"):
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
        elif self.backend in ["aws-postgres"]:
            import botocore  # type: ignore

            try:
                self.bucket.Object(file_path).load()
                return True
            except botocore.exceptions.ClientError as e:  # type: ignore
                if e.response["Error"]["Code"] == "404":
                    # The object does not exist.
                    return False
                else:
                    # Something else has gone wrong.
                    raise
        else:
            raise NotImplementedError(f"Backend {self.backend} is not implemented")

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
                    assert isinstance(data, str), "Must use JsonEncode for non-strings"
                    target_file.write(data)
        elif self.backend in ["aws-postgres"]:
            if json_encode:
                data = json.dumps(data)
            self.bucket.Object(filename).put(Body=data)
        else:
            raise NotImplementedError(f"Backend {self.backend} is not implemented")

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
        elif self.backend in ["aws-postgres"]:
            data = self.bucket.Object(filename).get()["Body"].read()
            if json_encoded:
                return json.loads(data)
            else:
                return data
        else:
            raise NotImplementedError(f"Backend {self.backend} is not implemented")

    def shutdown(self):
        if self.backend == "test":
            if self.made_temp_dir:
                shutil.rmtree(self.file_root)
