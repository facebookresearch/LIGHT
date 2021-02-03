#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sqlite3
import os
import csv
import random, itertools
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
from parlai.core.params import ParlaiParser
from light.data_model.conversation_checkpoint_parser import ConversationCheckpointParser
from light.data_model.environment_checkpoint_parser import EnvironmentCheckpointParser
from light.graph.utils import get_article
import sys
import parlai.utils.misc as parlai_utils
import json

sys.modules["parlai.core.utils"] = parlai_utils

# Edges between nodes stored in the database
DB_EDGE_IN_CONTAINED = "in_contained"
DB_EDGE_EX_CONTAINED = "ex_contained"
DB_EDGE_WORN = "worn"
DB_EDGE_WIELDED = "wielded"
DB_EDGE_NEIGHBOR = "neighbor"
DB_EDGE_CONTAINED_IN = "contained_in"  # new addition for obj containment
EDGE_TYPES = [
    DB_EDGE_IN_CONTAINED,
    DB_EDGE_EX_CONTAINED,
    DB_EDGE_CONTAINED_IN,
    DB_EDGE_WORN,
    DB_EDGE_WIELDED,
    DB_EDGE_NEIGHBOR,
]

DB_GRAPH_EDGE_CONTAINS = "contains"
DB_GRAPH_EDGE_NEIGHBOR_N = "neighbors to the north"
DB_GRAPH_EDGE_NEIGHBOR_E = "neighbors to the east"
DB_GRAPH_EDGE_NEIGHBOR_S = "neighbors to the south"
DB_GRAPH_EDGE_NEIGHBOR_W = "neighbors to the west"
DB_GRAPH_EDGE_NEIGHBOR_U = "neighbors above"
DB_GRAPH_EDGE_NEIGHBOR_D = "neighbors below"
DB_GRAPH_EDGE_WORN = "worn"
DB_GRAPH_EDGE_WIELDED = "wielded"
# Edges between nodes in graphs executed
GRAPH_EDGE_TYPES = [
    DB_GRAPH_EDGE_CONTAINS,
    DB_GRAPH_EDGE_NEIGHBOR_N,
    DB_GRAPH_EDGE_NEIGHBOR_E,
    DB_GRAPH_EDGE_NEIGHBOR_S,
    DB_GRAPH_EDGE_NEIGHBOR_W,
    DB_GRAPH_EDGE_NEIGHBOR_U,
    DB_GRAPH_EDGE_NEIGHBOR_D,
    DB_GRAPH_EDGE_WORN,
    DB_GRAPH_EDGE_WIELDED,
]

# All entity types existing in the database
DB_TYPE_BASE_CHAR = "base character"
DB_TYPE_CHAR = "character"
DB_TYPE_BASE_OBJ = "base object"
DB_TYPE_OBJ = "object"
DB_TYPE_BASE_ROOM = "base room"
DB_TYPE_ROOM = "room"
DB_TYPE_EDGE = "edge"
DB_TYPE_GRAPH_EDGE = "graph edge"
DB_TYPE_GRAPH_NODE = "graph node"
DB_TYPE_TEXT_EDGE = "text edge"
DB_TYPE_TILE = "tile"
DB_TYPE_INTERACTION = "interaction"
DB_TYPE_UTTERANCE = "utterance"
DB_TYPE_PARTICIPANT = "participant"
DB_TYPE_TURN = "turn"
DB_TYPE_PLAYER = "player"
DB_TYPE_WORLD = "world"
ENTITY_TYPES = [
    DB_TYPE_BASE_CHAR,
    DB_TYPE_CHAR,
    DB_TYPE_BASE_OBJ,
    DB_TYPE_OBJ,
    DB_TYPE_BASE_ROOM,
    DB_TYPE_ROOM,
    DB_TYPE_GRAPH_EDGE,
    DB_TYPE_GRAPH_NODE,
    DB_TYPE_EDGE,
    DB_TYPE_TEXT_EDGE,
    DB_TYPE_TILE,
    DB_TYPE_INTERACTION,
    DB_TYPE_UTTERANCE,
    DB_TYPE_PARTICIPANT,
    DB_TYPE_TURN,
    DB_TYPE_PLAYER,
    DB_TYPE_WORLD,
]

# Statuses for any content in the database
DB_STATUS_PROD = "production"
DB_STATUS_REVIEW = "under review"
DB_STATUS_REJECTED = "rejected"
DB_STATUS_QUESTIONABLE = "questionable"
DB_STATUS_ACCEPTED = "accepted"
# accepted one and accepted all are reserved for editing utterances,
# where there is the option to change the utterance only in the turn
# that the edit was submitted for or change the utterance in all places
# that it appears in. The choice is up to the reviewer.
DB_STATUS_ACCEPT_ONE = "accepted one"
DB_STATUS_ACCEPT_ALL = "accepted all"
DB_TRAIN_SPLIT = "train"
DB_TEST_SPLIT = "test"
DB_VAL_SPLIT = "val"
CONTENT_STATUSES = [
    DB_STATUS_PROD,
    DB_STATUS_REVIEW,
    DB_STATUS_REJECTED,
    DB_STATUS_QUESTIONABLE,
]
EDIT_STATUSES = [
    DB_STATUS_REVIEW,
    DB_STATUS_REJECTED,
    DB_STATUS_ACCEPTED,
    DB_STATUS_ACCEPT_ONE,
    DB_STATUS_ACCEPT_ALL,
]
DATASPLIT_TYPES = [
    DB_TRAIN_SPLIT,
    DB_TEST_SPLIT,
    DB_VAL_SPLIT,
]


def format_list_for_sql(list):
    return "{}".format(", ".join("('{}')".format(i) for i in list))


class LIGHTDatabase:
    def __init__(self, dbpath, read_only=False):
        argparser = ParlaiParser(False, False)
        # ignore unknown command line arguments
        opt = argparser.parse_and_process_known_args()[0]

        # Path to the database
        self.dbpath = dbpath
        conn = sqlite3.connect(self.dbpath)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = 1")
        c = conn.cursor()
        self.conn = conn
        self.c = c
        self.use_cache = False
        self.read_only = read_only
        self.cache = {}
        self.cache_init = False

        # Dictionary to convert between types in id_table and corresponding
        # table names
        self.table_dict = {
            DB_TYPE_BASE_CHAR: "base_characters_table",
            DB_TYPE_CHAR: "characters_table",
            DB_TYPE_BASE_OBJ: "base_objects_table",
            DB_TYPE_OBJ: "objects_table",
            DB_TYPE_BASE_ROOM: "base_rooms_table",
            DB_TYPE_ROOM: "rooms_table",
            DB_TYPE_TEXT_EDGE: "text_edges_table",
            DB_TYPE_EDGE: "node_content_table",
            DB_TYPE_GRAPH_EDGE: "edges_table",
            DB_TYPE_GRAPH_NODE: "nodes_table",
            DB_TYPE_TILE: "tile_table",
            DB_TYPE_INTERACTION: "interactions_table",
            DB_TYPE_UTTERANCE: "utterances_table",
            DB_TYPE_PARTICIPANT: "participants_table",
            DB_TYPE_TURN: "turns_table",
            DB_TYPE_PLAYER: "players_table",
            DB_TYPE_WORLD: "world_table",
        }

        if not self.read_only:
            # Master table for keeping unique IDs across tables and to look up
            # objects in the correct table given an ID
            self.c.execute(
                """
                CREATE TABLE IF NOT EXISTS id_table (
                    id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                    type text NOT NULL,
                    status text NOT NULL,
                    is_from_pickle BOOLEAN NOT NULL DEFAULT 0 CHECK
                        (is_from_pickle IN (0, 1)),
                    split text ,
                    CONSTRAINT fk_status FOREIGN KEY (status)
                        REFERENCES enum_table_status (status)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_split FOREIGN KEY (split)
                        REFERENCES enum_table_datasplit (split)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_id FOREIGN KEY (type)
                        REFERENCES enum_table_master_content (type)
                        ON DELETE CASCADE);
                """
            )
            # Enum table for types of contents in the master table (id_table)
            self.c.execute(
                """
                CREATE TABLE IF NOT EXISTS enum_table_master_content (
                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                type text NOT NULL UNIQUE);
                """
            )
            # Enum table for types of statuses in the master table (id_table)
            self.c.execute(
                """
                CREATE TABLE IF NOT EXISTS enum_table_status (
                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                status text NOT NULL UNIQUE);
                """
            )
            #  Enum table for types of data split in master table (id_table)
            self.c.execute(
                """
                CREATE TABLE IF NOT EXISTS enum_table_datasplit (
                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                split text NOT NULL UNIQUE);
                """
            )

            # Initialize content type enum table
            entity_types_formated = format_list_for_sql(ENTITY_TYPES)
            self.c.execute(
                """
                INSERT OR IGNORE INTO enum_table_master_content (type)
                VALUES {}
                """.format(
                    entity_types_formated
                )
            )

            # Initialize content status enum table
            content_statuses_formated = format_list_for_sql(CONTENT_STATUSES)
            self.c.execute(
                """
                INSERT OR IGNORE INTO enum_table_status (status)
                VALUES {}
                """.format(
                    content_statuses_formated
                )
            )

            #  Initialize data split type enum table
            datasplit_formated = format_list_for_sql(DATASPLIT_TYPES)
            self.c.execute(
                """
                INSERT OR IGNORE INTO enum_table_datasplit (split)
                VALUES {}
                """.format(
                    datasplit_formated
                )
            )

            # Initialize content status enum table
            edit_statuses_formated = format_list_for_sql(EDIT_STATUSES)
            self.c.execute(
                """
                INSERT OR IGNORE INTO enum_table_status (status)
                VALUES {}
                """.format(
                    edit_statuses_formated
                )
            )

            self.init_environment_tables()
            self.init_conversation_tables()
            self.init_edits_table()
            self.init_world_tables()
            self.init_user_tables()
            self.init_game_tables()
            self.create_triggers()
            self.check_custom_tags_objects_tables()

        # Dictionaries to convert between previous pickle IDs and current
        # database IDs
        self.id_char_dict = {}
        self.id_room_dict = {}
        self.id_object_dict = {}
        if read_only:
            self.create_cache()
        self.conn.commit()
        self.conn.close()

    # Connect to sqlite3 in __init__ instead because __init__ is called
    # before __enter__
    def create_cache(self):
        """Create a cached version of the database in dict format
        with id as the keys and the rows are values"""
        self.cache_init = True
        self.use_cache = True
        self.read_only = True

        try:
            possible_cache_path = self.dbpath + '.json'
            if os.path.exists(possible_cache_path):
                cache_date = os.path.getmtime(possible_cache_path)
                database_date = os.path.getmtime(self.dbpath)
                if cache_date > database_date:
                    with open(possible_cache_path, 'r') as json_cache:
                        self.cache = json.load(json_cache)
                        for key in self.cache.keys():
                            for str_id in self.cache[key].ids():
                                self.cache[key][int(str_id)] = self.cache[key][str_id]
                        return
        except Exception:
            pass  # initialize a new cache if the old one is corrupted

        db_table_dict = {
            "id": "id_table",
            "db_edges": "node_content_table",
            "text_edges": "text_edges_table",
            "characters": "characters_table",
            "rooms": "rooms_table",
            "objects": "objects_table",
            "base_chars": "base_characters_table",
            "base_rooms": "base_rooms_table",
            "base_objs": "base_objects_table",
            "worlds": "world_table",
        }

        for key, table_name in db_table_dict.items():
            self.c.execute("""SELECT * FROM {0};""".format(table_name))
            results = self.c.fetchall()
            if "edges" in key:
                self.cache[key] = {}
                for row in results:
                    if row["parent_id"] in self.cache[key]:
                        self.cache[key][int(row["parent_id"])].append(dict(row))
                    else:
                        self.cache[key][int(row["parent_id"])] = [dict(row)]
            else:
                self.cache[key] = {int(row["id"]): dict(row) for row in results}

        with open(possible_cache_path, 'w') as json_cache:
            json.dump(self.cache, json_cache)

    def __enter__(self):
        conn = sqlite3.connect(self.dbpath)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = 1")
        c = conn.cursor()
        self.conn = conn
        self.c = c
        return self

    def __exit__(self, type, value, trackback):
        # If there is a any type of error, rollback transaction
        if value != None:
            self.conn.rollback()
        self.conn.commit()
        self.conn.close()

    def load_dictionaries(self):
        """
        Loads dictionary mappings between IDs in pickles and IDs in the
        database, if the dictionaries are presennt
        """
        try:
            df = pd.read_csv(
                os.path.join(self.data_dir, "id_char_dict.csv"), header=None
            )
            self.id_char_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
            df = pd.read_csv(
                os.path.join(self.data_dir, "id_room_dict.csv"), header=None
            )
            self.id_room_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
            df = pd.read_csv(
                os.path.join(self.data_dir, "id_object_dict.csv"), header=None
            )
            self.id_object_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        except:
            print("Dictionaries for mappings are not present. ")

    def write_dictionaries(self):
        """Write dictionary of mappings to csv files"""
        df = pd.DataFrame.from_dict(self.id_char_dict, orient="index")
        df.to_csv(os.path.join(self.data_dir, "id_char_dict.csv"), header=False)
        df = pd.DataFrame.from_dict(self.id_room_dict, orient="index")
        df.to_csv(os.path.join(self.data_dir, "id_room_dict.csv"), header=False)
        df = pd.DataFrame.from_dict(self.id_object_dict, orient="index")
        df.to_csv(os.path.join(self.data_dir, "id_object_dict.csv"), header=False)

    def search_database(self, type, input, fts=True):
        """Search a specific table (dictated by 'type') using a search string"""
        table_name = self.table_dict[type]
        table_name_fts = self.table_dict[type] + "_fts"
        # if input is empty, return all entries of the specified type through
        # the "else" block

        try:
            self.c.execute(
                """
                SELECT * FROM {}
                WHERE name LIKE ?
                """.format(
                    table_name
                ),
                ("%" + input + "%",),
            )
            results = self.c.fetchall()
        except sqlite3.OperationalError:
            # Table cannot be searched by name
            results = []

        if fts and input != "":
            # Can use .format because table_name is being chosen from a predefined
            # list, so there is no risk for SQL injection
            self.c.execute(
                """
                SELECT *
                FROM {0}
                WHERE id IN (SELECT docid
                             FROM {1}
                             WHERE {1} MATCH ?);
                """.format(
                    table_name, table_name_fts
                ),
                (input,),
            )
            fts_results = self.c.fetchall()
            already_present = set(r['id'] for r in results)
            results += [r for r in fts_results if r['id'] not in already_present]

        return results

    def get_id(self, id=None, type=None, expand=False):
        """
        Get the type of entry associated with a particular ID by querying the
        id_table.
        """
        if self.use_cache and id is not None:
            use_id = int(id)
            if use_id in self.cache["id"]:
                found_id = self.cache["id"][use_id]
                if expand:
                    return [self.cache[found_id['type'] + 's'][use_id]]
                return [found_id]
        if self.use_cache and type is not None:
            return [row for row in self.cache["id"].values() if row["type"] == type]
        self.c.execute(
            """
            SELECT * FROM id_table
            WHERE (?1 IS NULL OR type = ?1)
            AND (?2 IS NULL OR id = ?2)
            """,
            (type, id),
        )
        ids = self.c.fetchall()
        if expand:
            return [self.get_query(i[0]) for i in ids]
        return ids

    def create_id(self, type, entry_attributes):
        is_from_pickle = False
        status = DB_STATUS_REVIEW
        if "is_from_pickle" in list(entry_attributes.keys()):
            is_from_pickle = entry_attributes["is_from_pickle"]
        if "status" in list(entry_attributes.keys()):
            status = entry_attributes["status"]
        if "split" in list(entry_attributes.keys()):
            split = entry_attributes["split"]
        if (
            set(list(entry_attributes.keys()))
            | set(["is_from_pickle", "status", "split"])
        ) > set(["is_from_pickle", "status", "split"]):
            raise Exception("Unrecognized keys in entry_attributes")
        if "split" in list(entry_attributes.keys()):
            # NOTE: this will break circleCI Unittest which will need to be updated to reflect the changes in Light DB
            self.c.execute(
                """
                INSERT INTO id_table (type, is_from_pickle, status, split) VALUES (?, ?, ?, ?)
                """,
                (type, is_from_pickle, status, split),
            )
        else:
            self.c.execute(
                """
                INSERT INTO id_table (type, is_from_pickle, status) VALUES (?, ?, ?)
                """,
                (type, is_from_pickle, status),
            )
        id = self.c.lastrowid
        if self.use_cache:
            self.c.execute("""SELECT * FROM id_table WHERE id = ?""", (id,))
            self.cache["id"][id] = self.c.fetchone()
        return id

    def delete_id(self, id):
        """
        Deletes specified id from id_table
        """
        self.c.execute("DELETE FROM id_table WHERE id = ?", (id,))
        if self.use_cache and id in self.cache["id"]:
            del self.cache["id"][id]

    def update_status(self, id, status):
        """Updates status of entity in the database"""
        assert status in CONTENT_STATUSES
        self.c.execute(
            """
            UPDATE id_table
            SET status = ?
            WHERE id = ?;
            """,
            (status, id),
        )
        if self.use_cache and id in self.cache["id"]:
            self.c.execute("""SELECT * FROM id_table WHERE id = ? """, (id,))
            self.cache["id"][id] = self.c.fetchone()

    def update_split(self, id, split):
        """Updates status of entity in the database"""
        assert split in DATASPLIT_TYPES
        self.c.execute(
            """
            UPDATE id_table
            SET split = ?
            WHERE id = ?;
            """,
            (split, id),
        )
        if self.use_cache and id in self.cache["id"]:
            self.c.execute("""SELECT * FROM id_table WHERE id = ? """, (id,))
            self.cache["id"][id] = self.c.fetchone()

    def get_columns(self, type):
        """
        Takes "type" as specified by keys in table_dictionary and returns a
        dictionary where the keys are the column names and the values are the
        column types
        """
        assert type in list(self.table_dict.keys()), "Type is invalid"
        table_name = self.table_dict[type]
        self.c.execute(f"PRAGMA table_info({table_name})")
        fetched = self.c.fetchall()
        result = {i[1]: i[2] for i in fetched}
        return result

    def table_not_exists(self, table_name):
        self.c.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type="table" AND name=?;
            """,
            (table_name,),
        )
        return self.c.fetchone() == None

    def init_environment_tables(self):
        """
        Initializes environment tables. All IDs are unique across different
        types of content.
        """
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS enum_table_edge_type (
            id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            type text NOT NULL UNIQUE);
            """
        )
        # Base object types
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS base_objects_table (
            id integer PRIMARY KEY NOT NULL,
            name text NOT NULL UNIQUE,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )
        table_not_exists = self.table_not_exists("base_objects_table_fts")
        # FTS table for base objects
        self.c.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS base_objects_table_fts
            USING fts4(tokenize=porter, content="base_objects_table", name);
            """
        )
        # Required to link existing objects
        if table_not_exists:
            self.c.execute(
                """
                INSERT INTO "base_objects_table_fts" (rowid, name)
                    SELECT rowid, name FROM base_objects_table;
                """
            )
        # Specific objects created from object types
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS objects_table (
            id integer PRIMARY KEY NOT NULL,
            name text NOT NULL,
            base_id integer NOT NULL,
            /* attributes */
            is_container real NOT NULL,
            is_drink real NOT NULL,
            is_food real NOT NULL,
            is_gettable real NOT NULL,
            is_surface real NOT NULL,
            is_wearable real NOT NULL,
            is_weapon real NOT NULL,
            physical_description text NOT NULL,
            name_prefix text NOT NULL,
            is_plural float NOT NULL,
            size integer,
            contain_size integer,
            shape text,
            value integer,
            UNIQUE (name, base_id, physical_description),
            CONSTRAINT fk_base_id FOREIGN KEY (base_id)
                REFERENCES base_objects_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )
        table_not_exists = self.table_not_exists("objects_table_fts")
        self.c.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS objects_table_fts
            USING fts4(tokenize=porter, content="objects_table", name, physical_description);
            """
        )
        if table_not_exists:
            self.c.execute(
                """
                INSERT INTO "objects_table_fts" (rowid, name, physical_description)
                    SELECT rowid, name, physical_description FROM objects_table;
                """
            )

        # Basic room types
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS base_rooms_table (
            id integer PRIMARY KEY NOT NULL,
            name text NOT NULL UNIQUE,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )
        table_not_exists = self.table_not_exists("base_rooms_table_fts")
        # FTS table for base rooms
        self.c.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS base_rooms_table_fts
            USING fts4(tokenize=porter, content="base_rooms_table", name);
            """
        )
        if table_not_exists:
            self.c.execute(
                """
                INSERT INTO "base_rooms_table_fts" (rowid, name)
                    SELECT rowid, name FROM base_rooms_table;
                """
            )
        # Specific rooms created from room types
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms_table (
            id integer PRIMARY KEY NOT NULL,
            name text NOT NULL,
            base_id integer NOT NULL,
            description text NOT NULL,
            backstory text NOT NULL,
            UNIQUE (name, base_id, description, backstory),
            CONSTRAINT fk_base_id
                FOREIGN KEY (base_id)
                REFERENCES base_rooms_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_id
                FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )
        table_not_exists = self.table_not_exists("rooms_table_fts")
        # FTS table for rooms
        self.c.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS rooms_table_fts
            USING fts4(tokenize=porter, content="rooms_table", name, description, backstory);
            """
        )
        if table_not_exists:
            self.c.execute(
                """
                INSERT INTO "rooms_table_fts" (rowid, name, description, backstory)
                    SELECT rowid, name, description, backstory FROM rooms_table;
                """
            )
        # Basic character types
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS base_characters_table (
            id integer PRIMARY KEY NOT NULL,
            name text NOT NULL UNIQUE,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )
        table_not_exists = self.table_not_exists("base_characters_table_fts")
        # FTS table for base characters
        self.c.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS base_characters_table_fts
            USING fts4(tokenize=porter, content="base_characters_table", name);
            """
        )
        if table_not_exists:
            self.c.execute(
                """
                INSERT INTO "base_characters_table_fts" (rowid, name)
                    SELECT rowid, name FROM base_characters_table;
                """
            )
        # Specific characters created from character types
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS characters_table (
            id integer PRIMARY KEY NOT NULL,
            name text NOT NULL,
            base_id integer NOT NULL,
            persona text NOT NULL,
            physical_description text NOT NULL,
            name_prefix text NOT NULL,
            is_plural float NOT NULL,
            char_type text NOT NULL,
            UNIQUE (name, base_id, persona, physical_description),
            CONSTRAINT fk_base_id
                FOREIGN KEY (base_id)
                REFERENCES base_characters_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_id
                FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )
        table_not_exists = self.table_not_exists("characters_table_fts")
        # FTS table for characters
        self.c.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS characters_table_fts
            USING fts4(tokenize=porter, content="characters_table", name, persona, physical_description);
            """
        )
        if table_not_exists:
            self.c.execute(
                """
                INSERT INTO "characters_table_fts" (rowid, name, persona, physical_description)
                    SELECT rowid, name, persona, physical_description FROM characters_table;
                """
            )
        # Node contents represent an edge between a node and something in it
        # Edge is deleted when either node is deleted
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS node_content_table (
            id integer PRIMARY KEY NOT NULL,
            parent_id integer NOT NULL,
            child_id integer NOT NULL,
            edge_type text NOT NULL,
            edge_strength BOOLEAN NOT NULL CHECK
                (edge_strength IN (0, 1)),
            UNIQUE (parent_id, child_id, edge_type, edge_strength),
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_id1 FOREIGN KEY (parent_id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_id2 FOREIGN KEY (child_id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_edge FOREIGN KEY (edge_type)
                REFERENCES enum_table_edge_type (type)
                ON DELETE CASCADE);
            """
        )
        # Text edges table stores edges between an  an object in the dataset
        # and text that represents something that isn't in the dataset yet
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS text_edges_table (
            id integer PRIMARY KEY NOT NULL,
            parent_id integer NOT NULL,
            child_text text NOT NULL,
            child_desc text NOT NULL,
            child_label text NOT NULL,
            edge_type text NOT NULL,
            edge_strength BOOLEAN NOT NULL CHECK
                (edge_strength IN (0, 1)),
            UNIQUE (parent_id, child_text, child_desc, child_label,
                edge_type, edge_strength),
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_id1 FOREIGN KEY (parent_id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_edge FOREIGN KEY (edge_type)
                REFERENCES enum_table_edge_type (type)
                ON DELETE CASCADE);
            """
        )
        if not self.read_only:
            # Initialize edge type enum table
            edge_types_formated = format_list_for_sql(EDGE_TYPES)
            self.c.execute(
                """
                INSERT OR IGNORE INTO enum_table_edge_type (type)
                VALUES {}
                """.format(
                    edge_types_formated
                )
            )

    def create_base_character(self, name, entry_attributes={}):
        id = self.create_id(DB_TYPE_BASE_CHAR, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO base_characters_table (id, name) VALUES (?, ?)
            """,
            (id, name),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from base_characters_table WHERE name = ?
                """,
                (name,),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, False)

    def create_character(
        self,
        name,
        base_id,
        persona,
        physical_description,
        entry_attributes={},
        name_prefix=None,
        is_plural=None,
        char_type="unknown",
    ):
        # Inherit name from base character if no name is provided
        if name == None:
            self.c.execute(
                """
                SELECT name FROM base_characters_table WHERE id = ?
                """,
                (base_id,),
            )
            # fetchall() returns format [(<name>,)]
            result = self.c.fetchall()
            assert len(result) == 1
            name = result[0][0]

        # If name prefix is None, guess heuristically
        if name_prefix is None:
            name_prefix = get_article(name)

        # If plurality is None, guess heuristically
        if is_plural is None:
            is_plural = 0 if name[-1] != "s" else 0.7

        id = self.create_id(DB_TYPE_CHAR, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO characters_table(id, name, base_id, persona,
            physical_description, name_prefix, is_plural, char_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id,
                name,
                base_id,
                persona,
                physical_description,
                name_prefix,
                is_plural,
                char_type,
            ),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from characters_table WHERE name = ? AND base_id = ? \
                AND persona = ? AND physical_description = ?
                """,
                (name, base_id, persona, physical_description),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_base_object(self, name, entry_attributes={}):
        id = self.create_id(DB_TYPE_BASE_OBJ, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO base_objects_table (id, name) VALUES (?, ?)
            """,
            (id, name),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from base_objects_table WHERE name = ?
                """,
                (name,),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_object(
        self,
        name,
        base_id,
        is_container,
        is_drink,
        is_food,
        is_gettable,
        is_surface,
        is_wearable,
        is_weapon,
        physical_description,
        entry_attributes={},
        name_prefix=None,
        is_plural=None,
        size=None,
        contain_size=None,
        shape=None,
        value=None
    ):
        # Check that the attributes are between 0 and 1
        assert (
            float(is_container) >= 0 and float(is_container) <= 1
        ), "is_container value must be a float between 0 and 1"
        assert (
            float(is_drink) >= 0 and float(is_drink) <= 1
        ), "is_drink value must be a float between 0 and 1"
        assert (
            float(is_food) >= 0 and float(is_food) <= 1
        ), "is_food value must be a float between 0 and 1"
        assert (
            float(is_gettable) >= 0 and float(is_gettable) <= 1
        ), "is_gettable value must be a float between 0 and 1"
        assert (
            float(is_surface) >= 0 and float(is_surface) <= 1
        ), "is_surface value must be a float between 0 and 1"
        assert (
            float(is_wearable) >= 0 and float(is_wearable) <= 1
        ), "is_wearable value must be a float between 0 and 1"
        assert (
            float(is_weapon) >= 0 and float(is_weapon) <= 1
        ), "is_weapon value must be a float between 0 and 1"
        # If name is null, inherit name from base class
        if name == None:
            self.c.execute(
                """
                SELECT name FROM base_objects_table WHERE id = ?
                """,
                (base_id,),
            )
            # fetchall() returns format [(<name>,)]
            result = self.c.fetchall()
            assert len(result) == 1
            name = result[0][0]

        # If name prefix is None, guess heuristically
        if name_prefix is None:
            name_prefix = get_article(name)

        # If plurality is None, guess heuristically
        if is_plural is None:
            is_plural = 0 if name[-1] != "s" else 0.7

        # Attempt insert
        choice = random.randint(0, 9)
        if choice < 8:
            entry_attributes["split"] = "train"
        elif choice == 8:
            entry_attributes["split"] = "test"
        else:
            entry_attributes["split"] = "val"

        id = self.create_id(DB_TYPE_OBJ, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO objects_table(id, name, base_id, is_container,
            is_drink, is_food, is_gettable, is_surface, is_wearable, is_weapon,
            physical_description, name_prefix, is_plural, size, contain_size, shape, value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id,
                name,
                base_id,
                is_container,
                is_drink,
                is_food,
                is_gettable,
                is_surface,
                is_wearable,
                is_weapon,
                physical_description,
                name_prefix,
                is_plural,
                size,
                contain_size,
                shape,
                value
            ),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from objects_table WHERE name = ? AND base_id = ? \
                AND is_container = ? AND is_drink = ? AND is_food = ? \
                AND is_gettable = ? AND is_surface = ? AND is_wearable = ? \
                AND is_weapon = ? AND physical_description = ? \
                AND size = ? AND contain_size = ? AND shape = ? AND value = ? \
                """,
                (
                    name,
                    base_id,
                    is_container,
                    is_drink,
                    is_food,
                    is_gettable,
                    is_surface,
                    is_wearable,
                    is_weapon,
                    physical_description,
                    size,
                    contain_size,
                    shape,
                    value
                ),
            )
            result = self.c.fetchall()
            assert (
                len(result) == 1
            ), "There is already an existing item with these unique IDs (name, base_id, physical_description)"
            id = int(result[0][0])
        return (id, inserted)

    def create_base_room(self, name, entry_attributes={}):
        id = self.create_id(DB_TYPE_BASE_ROOM, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO base_rooms_table (id, name) VALUES (?, ?)
            """,
            (id, name),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from base_rooms_table WHERE name = ?
                """,
                (name,),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_room(self, name, base_id, description, backstory, entry_attributes={}):
        # Inherit name from base room if no name is provided
        if name == None:
            self.c.execute(
                """
                SELECT name FROM base_rooms_table WHERE id = ?
                """,
                (base_id,),
            )
            # fetchall() returns format [(<name>,)]
            result = self.c.fetchall()
            assert len(result) == 1
            name = result[0][0]
        choice = random.randint(0, 9)
        if choice < 8:
            entry_attributes["split"] = "train"
        elif choice == 8:
            entry_attributes["split"] = "test"
        else:
            entry_attributes["split"] = "val"
        id = self.create_id(DB_TYPE_ROOM, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO \
            rooms_table(id, name, base_id, description, backstory)
            VALUES (?, ?, ?, ?, ?)
            """,
            (id, name, base_id, description, backstory),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from rooms_table WHERE name = ? AND base_id = ? \
                AND description = ? AND backstory = ?
                """,
                (name, base_id, description, backstory),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_node_content(
        self, parent_id, child_id, edge_type, edge_strength, entry_attributes={}
    ):
        id = self.create_id(DB_TYPE_EDGE, entry_attributes)
        # TODO force creating edges when one or more nodes are missing.
        # Problem: if an entity is missing from master ID table, we cannot tell
        # what type of node it is supposed to be (character, room, object)
        assert self.get_id(parent_id)[0][1] in ["character", "object", "room"]
        self.c.execute(
            """
            INSERT or IGNORE INTO node_content_table(id, parent_id, child_id,
            edge_type, edge_strength)
            VALUES (?, ?, ?, ?, ?)
            """,
            (id, parent_id, child_id, edge_type, edge_strength),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from node_content_table WHERE parent_id = ? AND child_id = ? \
                AND edge_type = ? AND edge_strength = ?
                """,
                (parent_id, child_id, edge_type, edge_strength),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_text_edge(
        self,
        parent_id,
        child_text,
        edge_type,
        edge_strength,
        entry_attributes={},
        child_desc="",
        child_label="",
    ):
        id = self.create_id(DB_TYPE_TEXT_EDGE, entry_attributes)
        assert parent_id == None or self.get_id(parent_id)[0][1] in [
            DB_TYPE_CHAR,
            DB_TYPE_OBJ,
            DB_TYPE_ROOM,
        ]
        self.c.execute(
            """
            INSERT or IGNORE INTO text_edges_table(id, parent_id, child_text,
            child_desc, child_label, edge_type, edge_strength)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id,
                parent_id,
                child_text,
                child_desc,
                child_label,
                edge_type,
                edge_strength,
            ),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from text_edges_table WHERE parent_id = ? AND child_text = ? \
                AND child_desc = ? AND child_label = ? AND edge_type = ? AND edge_strength = ?
                """,
                (
                    parent_id,
                    child_text,
                    child_desc,
                    child_label,
                    edge_type,
                    edge_strength,
                ),
            )
            result = self.c.fetchall()
            assert (
                len(result) == 1
            ), f"had more than one result: {result}, {child_text}, {parent_id}"
            id = int(result[0][0])
        return (id, inserted)

    def get_base_character(self, id=None, name=None):
        self.c.execute(
            """
            SELECT * FROM base_characters_table
            WHERE (?1 IS NULL OR name = ?1)
            AND (?2 IS NULL OR id = ?2)
            """,
            (name, id),
        )
        return self.c.fetchall()

    def get_character(
        self, id=None, name=None, base_id=None, persona=None, physical_description=None
    ):
        if self.use_cache:
            if id is not None and id in self.cache["characters"]:
                return [self.cache["characters"][id]]
        self.c.execute(
            """
            SELECT * FROM characters_table
            WHERE (?1 IS NULL OR name = ?1)
            AND (?2 IS NULL OR base_id = ?2)
            AND (?3 IS NULL OR persona = ?3)
            AND (?4 IS NULL OR physical_description = ?4)
            AND (?5 IS NULL OR id = ?5)
            """,
            (name, base_id, persona, physical_description, id),
        )
        return self.c.fetchall()

    def get_base_object(self, id=None, name=None):
        self.c.execute(
            """
            SELECT * FROM base_objects_table
            WHERE (?1 IS NULL OR name = ?1)
            AND (?2 IS NULL OR id = ?2)
            """,
            (name, id),
        )
        return self.c.fetchall()

    def get_object(
        self,
        id=None,
        name=None,
        base_id=None,
        is_container=None,
        is_drink=None,
        is_food=None,
        is_gettable=None,
        is_surface=None,
        is_wearable=None,
        is_weapon=None,
        physical_description=None,
        size=None,
        contain_size=None,
        shape=None,
        value=None,
    ):
        if self.use_cache and id is not None and id in self.cache["objects"]:
            return [self.cache["objects"][id]]
        self.c.execute(
            """
            SELECT * from objects_table
            WHERE (?1 IS NULL OR name = ?1)
            AND (?2 IS NULL OR base_id = ?2)
            AND (?3 IS NULL OR is_container = ?3)
            AND (?4 IS NULL OR is_drink = ?4)
            AND (?5 IS NULL OR is_food = ?5)
            AND (?6 IS NULL OR is_gettable = ?6)
            AND (?7 IS NULL OR is_surface = ?7)
            AND (?8 IS NULL OR is_wearable = ?8)
            AND (?9 IS NULL OR is_weapon = ?9)
            AND (?10 IS NULL OR physical_description = ?10)
            AND (?11 IS NULL OR size = ?11)
            AND (?12 IS NULL OR contain_size = ?12)
            AND (?13 IS NULL OR shape = ?13)
            AND (?14 IS NULL OR value = ?14)
            AND (?15 IS NULL OR id = ?15)
            """,
            (
                name,
                base_id,
                is_container,
                is_drink,
                is_food,
                is_gettable,
                is_surface,
                is_wearable,
                is_weapon,
                physical_description,
                size,
                contain_size,
                shape,
                value,
                id,
            ),
        )
        return self.c.fetchall()

    def get_base_room(self, id=None, name=None):
        self.c.execute(
            """
            SELECT * FROM base_rooms_table
            WHERE (?1 IS NULL OR name = ?1)
            AND (?2 IS NULL OR id = ?2)
            """,
            (name, id),
        )
        return self.c.fetchall()

    def get_room(
        self, id=None, name=None, base_id=None, description=None, backstory=None
    ):
        if self.use_cache:
            if id is not None and id in self.cache["rooms"]:
                return [self.cache["rooms"][id]]

        self.c.execute(
            """
            SELECT * FROM rooms_table
            WHERE (?1 IS NULL OR name = ?1)
            AND (?2 IS NULL OR base_id = ?2)
            AND (?3 IS NULL OR description = ?3)
            AND (?4 IS NULL OR backstory = ?4)
            AND (?5 IS NULL OR id = ?5)
            """,
            (name, base_id, description, backstory, id),
        )
        return self.c.fetchall()

    def get_node_content(
        self, id=None, parent_id=None, child_id=None, edge_type=None, edge_strength=None
    ):
        if self.use_cache:
            results = self.get_edges_cached("db_edges", parent_id, edge_type)
            if len(results):
                return results
        self.c.execute(
            """
            SELECT * FROM node_content_table
            WHERE (?1 IS NULL OR parent_id = ?1)
            AND (?2 IS NULL OR child_id = ?2)
            AND (?3 IS NULL OR edge_type = ?3)
            AND (?4 IS NULL OR edge_strength = ?4)
            AND (?5 IS NULL OR id = ?5)
            """,
            (parent_id, child_id, edge_type, edge_strength, id),
        )
        return self.c.fetchall()

    def get_text_edge(
        self,
        id=None,
        parent_id=None,
        child_text=None,
        edge_type=None,
        edge_strength=None,
    ):
        if self.use_cache:
            results = self.get_edges_cached("text_edges", parent_id, edge_type)
            if len(results):
                return results

        self.c.execute(
            """
            SELECT * FROM text_edges_table
            WHERE (?1 IS NULL OR parent_id = ?1)
            AND (?2 IS NULL OR child_text = ?2)
            AND (?3 IS NULL OR edge_type = ?3)
            AND (?4 IS NULL OR edge_strength = ?4)
            AND (?5 IS NULL OR id = ?5)
            """,
            (parent_id, child_text, edge_type, edge_strength, id),
        )
        return self.c.fetchall()

    def get_edges_cached(self, cache_key, parent_id=None, edge_type=None):
        results = []
        if parent_id is not None:
            results = self.cache[cache_key][parent_id]
        if edge_type is not None:
            if len(results) == 0:
                results = self.cache[cache_key].values()
                results = list(
                    itertools.chain.from_iterable([rows for rows in results])
                )
            results = [r for r in results if r["edge_type"] == edge_type]
        return results

    def init_user_tables(self):
        """
        Initializes users and login tables
        """
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS user_table (
            id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            username text UNIQUE NOT NULL);
            """
        )

        # NOTE: In future, if memberships / premium status type stuff or more login tables
        # that could be included here!

    def init_world_tables(self):
        """
        Initializes world tables
        """
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS world_table (
            id integer PRIMARY KEY NOT NULL,
            name text NOT NULL,
            owner_id integer NOT NULL,
            height integer NOT NULL,
            width integer NOT NULL,
            num_floors integer NOT NULL,
            in_use BOOLEAN NOT NULL CHECK (in_use IN (0, 1)),
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_user FOREIGN KEY (owner_id)
                REFERENCES user_table (id)
                ON DELETE CASCADE);
            """
        )

        # Store 1 autosave per user in this table
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS auto_save_table (
            owner_id integer PRIMARY KEY NOT NULL UNIQUE,
            timestamp TEXT NOT NULL,
            world_dump TEXT NOT NULL,
            CONSTRAINT fk_user FOREIGN KEY (owner_id)
                REFERENCES user_table (id)
                ON DELETE CASCADE);
            """
        )

        # Differs from text_edges as those are more annotation, these are actual edges of
        # world graphs in execution
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS enum_table_graph_edge_type (
            id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            type text NOT NULL UNIQUE);
            """
        )
        # Initialize the graph edge type enum table
        graph_edge_types_formated = format_list_for_sql(GRAPH_EDGE_TYPES)
        self.c.execute(
            """
            INSERT OR IGNORE INTO enum_table_graph_edge_type (type)
            VALUES {}
            """.format(
                graph_edge_types_formated
            )
        )

        # Initialize the graph nodes table
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS nodes_table (
            id integer PRIMARY KEY NOT NULL,
            w_id integer NOT NULL,
            entity_id integer NOT NULL,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_graph FOREIGN KEY (w_id)
                REFERENCES world_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_eid FOREIGN KEY (entity_id)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )

        # Graph edges table - edges in execution
        # (need src, dst, type of node - can we just have
        # Edge North, Edge South, Edge West, Edge East, Edge Up, Edge Down, Edge contains?)
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS edges_table (
            id integer PRIMARY KEY NOT NULL,
            w_id integer NOT NULL,
            src_id integer NOT NULL,
            dst_id integer NOT NULL,
            edge_type text NOT NULL,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_id FOREIGN KEY (w_id)
                REFERENCES world_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_src FOREIGN KEY (src_id)
                REFERENCES nodes_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_dst FOREIGN KEY (dst_id)
                REFERENCES nodes_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_edge FOREIGN KEY (edge_type)
                REFERENCES enum_table_graph_edge_type (type)
                ON DELETE CASCADE);
            """
        )

        # Tiles table - needs node/room id that goes inside too(?)
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS tile_table (
            id integer PRIMARY KEY NOT NULL,
            world_id integer NOT NULL,
            room_node_id integer NOT NULL,
            color integer NOT NULL,
            x_coordinate integer NOT NULL,
            y_coordinate integer NOT NULL,
            floor integer NOT NULL,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_world FOREIGN KEY (world_id)
                REFERENCES world_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_room FOREIGN KEY (room_node_id)
                REFERENCES nodes_table (id)
                ON DELETE CASCADE);
            """
        )

    def init_conversation_tables(self):
        """
        Initializes conversation tables. All IDs are unique across different
        types of content.
        """
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS enum_interaction_type (
            id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            type text NOT NULL UNIQUE);
            """
        )
        # Interaction contains setting id and will eventually contain
        # game state initialization data
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions_table (
            id integer PRIMARY KEY NOT NULL,
            setting_id integer NOT NULL,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_setting_id FOREIGN KEY (setting_id)
                REFERENCES rooms_table (id)
                ON DELETE CASCADE);
            """
        )
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS utterances_table (
            id integer PRIMARY KEY NOT NULL,
            dialogue text NOT NULL UNIQUE,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )
        table_not_exists = self.table_not_exists("utterances_table_fts")
        # FTS table for utterances
        self.c.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS utterances_table_fts
            USING fts4(tokenize=porter, content="utterances_table", dialogue);
            """
        )
        if table_not_exists:
            self.c.execute(
                """
                INSERT INTO "utterances_table_fts" (rowid, dialogue)
                    SELECT rowid, dialogue FROM utterances_table;
                """
            )
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS participants_table (
            id integer PRIMARY KEY NOT NULL,
            interaction_id integer NOT NULL,
            character_id integer not NULL,
            player_id integer not NULL,
            UNIQUE (interaction_id, character_id, player_id),
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_interaction FOREIGN KEY (interaction_id)
                REFERENCES interactions_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_character FOREIGN KEY (character_id)
                REFERENCES characters_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_player FOREIGN KEY (player_id)
                REFERENCES players_table (id)
                ON DELETE CASCADE);
            """
        )
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS turns_table (
            id integer PRIMARY KEY NOT NULL,
            interaction_id integer NOT NULL,
            turn_number integer NOT NULL,
            turn_time integer NOT NULL,
            interaction_type text NOT NULL,
            /* utterance_id is None for actions or emotes */
            utterance_id integer,
            /* action is None for speeches */
            action text,
            speaker_id integer not NULL,
            listener_id integer,
            /* Each unique interaction will have different interaction_id and
            turn_number */
            UNIQUE (interaction_id, turn_number),
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_interaction FOREIGN KEY (interaction_id)
                REFERENCES interactions_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_interaction_id FOREIGN KEY (interaction_type)
                REFERENCES enum_interaction_type (type)
                ON DELETE CASCADE,
            CONSTRAINT fk_utterance FOREIGN KEY (utterance_id)
                REFERENCES utterances_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_speaker FOREIGN KEY (speaker_id)
                REFERENCES participants_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_listener FOREIGN KEY (listener_id)
                REFERENCES participants_table (id)
                ON DELETE CASCADE);
            """
        )
        table_not_exists = self.table_not_exists("turns_table_fts")
        # FTS table for turns
        self.c.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS turns_table_fts
            USING fts4(tokenize=porter, content="turns_table", interaction_type, action);
            """
        )
        if table_not_exists:
            self.c.execute(
                """
                INSERT INTO "turns_table_fts" (rowid, interaction_type, action)
                    SELECT rowid, interaction_type, action FROM turns_table;
                """
            )
        # Table to represent all players of the game
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS players_table (
            id integer PRIMARY KEY NOT NULL,
            CONSTRAINT fk_id FOREIGN KEY (id)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )
        if not self.read_only:
            # Enum table to represent interaction types
            self.c.execute(
                """
                INSERT OR IGNORE INTO enum_interaction_type (type)
                VALUES ('action'), ('emote'), ('speech')
                """
            )

    def create_interaction(self, setting_id, entry_attributes={}):
        id = self.create_id(DB_TYPE_INTERACTION, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO interactions_table (id, setting_id) VALUES \
            (?, ?)
            """,
            (id, setting_id),
        )
        return (id, True)

    def create_utterance(self, dialogue, entry_attributes={}):
        id = self.create_id(DB_TYPE_UTTERANCE, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO utterances_table (id, dialogue) VALUES (?, ?)
            """,
            (id, dialogue),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from utterances_table WHERE dialogue = ?
                """,
                (dialogue,),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_participant(
        self, interaction_id, character_id, player_id, entry_attributes={}
    ):
        id = self.create_id(DB_TYPE_PARTICIPANT, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO participants_table (id, interaction_id,
            character_id, player_id)
            VALUES (?, ?, ?, ?)
            """,
            (id, interaction_id, character_id, player_id),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from participants_table WHERE interaction_id = ? AND \
                character_id = ? AND player_id = ?
                """,
                (interaction_id, character_id, player_id),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_turn(
        self,
        interaction_id,
        turn_number,
        turn_time,
        interaction_type,
        utterance_id,
        action,
        speaker_id,
        listener_id,
        entry_attributes={},
    ):
        id = self.create_id(DB_TYPE_TURN, entry_attributes)
        self.c.execute(
            """
            INSERT OR IGNORE INTO turns_table (id, interaction_id, turn_number,
            turn_time, interaction_type, utterance_id, action, speaker_id,
            listener_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id,
                interaction_id,
                turn_number,
                turn_time,
                interaction_type,
                utterance_id,
                action,
                speaker_id,
                listener_id,
            ),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from turns_table WHERE interaction_id = ? AND \
                turn_number = ?
                """,
                (interaction_id, turn_number),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_player(self, entry_attributes={}):
        id = self.create_id(DB_TYPE_PLAYER, entry_attributes)
        self.c.execute("INSERT INTO players_table (id) VALUES (?)", (id,))
        return (id, True)

    def get_interaction(self, id=None, setting_id=None):
        self.c.execute(
            """
            SELECT * FROM interactions_table
            WHERE (?1 IS NULL OR setting_id = ?1)
            AND (?2 IS NULL OR id = ?2)
            """,
            (setting_id, id),
        )
        return self.c.fetchall()

    def get_utterance(self, id=None, dialogue=None):
        self.c.execute(
            """
            SELECT * FROM utterances_table
            WHERE (?1 IS NULL OR dialogue = ?1)
            AND (?2 IS NULL OR id = ?2)
            """,
            (dialogue, id),
        )
        return self.c.fetchall()

    def get_participant(
        self, id=None, interaction_id=None, character_id=None, player_id=None
    ):
        self.c.execute(
            """
            SELECT * FROM participants_table
            WHERE (?1 IS NULL OR interaction_id = ?1)
            AND (?2 IS NULL OR character_id = ?2)
            AND (?3 IS NULL OR player_id = ?3)
            AND (?4 IS NULL OR id = ?4)
            """,
            (interaction_id, character_id, player_id, id),
        )
        return self.c.fetchall()

    def get_turn(
        self,
        id=None,
        interaction_id=None,
        turn_number=None,
        turn_time=None,
        interaction_type=None,
        utterance_id=None,
        action=None,
        speaker_id=None,
        listener_id=None,
    ):
        self.c.execute(
            """
            SELECT * FROM turns_table
            WHERE (?1 IS NULL OR interaction_id = ?1)
            AND (?2 IS NULL OR turn_number = ?2)
            AND (?3 IS NULL OR turn_time = ?3)
            AND (?4 IS NULL OR interaction_type = ?4)
            AND (?5 IS NULL OR utterance_id = ?5)
            AND (?6 IS NULL OR action = ?6)
            AND (?7 IS NULL OR speaker_id = ?7)
            AND (?8 IS NULL OR listener_id = ?8)
            AND (?9 IS NULL OR id = ?9)
            """,
            (
                interaction_id,
                turn_number,
                turn_time,
                interaction_type,
                utterance_id,
                action,
                speaker_id,
                listener_id,
                id,
            ),
        )
        return self.c.fetchall()

    def get_player(self, id=None):
        self.c.execute(
            """
            SELECT * FROM players_table
            WHERE (?1 IS NULL OR id = ?1)
            """,
            (id,),
        )
        return self.c.fetchall()

    # TODO revisit and finalize this format when actually
    # saving worlds
    def init_game_tables(self):
        """
        Initialize tables necessary for saving a complete game
        """
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS games_table (
            game_id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            graph text NOT NULL,
            creator int NOT NULL,
            CONSTRAINT fk_creator FOREIGN KEY (creator)
                REFERENCES players_table (id)
                ON DELETE CASCADE);
            """
        )
        self.c.execute(
            """
              CREATE TABLE IF NOT EXISTS enum_table_directions (
              id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
              direction text NOT NULL UNIQUE);
              """
        )
        self.c.execute(
            """
              INSERT OR IGNORE INTO enum_table_directions (direction)
              VALUES ('N'), ('S'), ('W'), ('E')
              """
        )
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS game_components_table (
            component_id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            game int NOT NULL,
            component int NOT NULL,
            CONSTRAINT fk_game FOREIGN KEY (game)
                REFERENCES games_table (game_id)
                ON DELETE CASCADE
            CONSTRAINT fk_component FOREIGN KEY (component)
                REFERENCES id_table (id)
                ON DELETE CASCADE);
            """
        )
        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS game_edges_table (
            edge_id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            game int NOT NULL,
            parent int NOT NULL,
            child int NOT NULL,
            edge int NOT NULL,
            direction text DEFAULT null,
            CONSTRAINT fk_game FOREIGN KEY (game)
                REFERENCES games_table (game_id)
                ON DELETE CASCADE,
            CONSTRAINT fk_edge FOREIGN KEY (edge)
                REFERENCES node_content_table (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_direction FOREIGN KEY (direction)
                REFERENCES enum_table_directions (direction)
                ON DELETE CASCADE);
            """
        )

    def get_games(self, game_id=None, graph=None, creator=None):
        """
        Retrieves games that satisfy the given constraints
        """
        self.c.execute(
            """
            SELECT * FROM games_table
            WHERE (?1 IS NULL OR game_id = ?1)
            AND (?2 IS NULL OR graph = ?2)
            AND (?3 IS NULL OR creator = ?3)
            """,
            (game_id, graph, creator),
        )
        return self.c.fetchall()

    def get_game_components(self, component_id=None, game=None, component=None):
        """
        Retrieves game components that satisfy the given constraints
        """
        self.c.execute(
            """
            SELECT * FROM game_components_table
            WHERE (?1 IS NULL OR component_id = ?1)
            AND (?2 IS NULL OR game = ?2)
            AND (?3 IS NULL OR component = ?3)
            """,
            (component_id, game, component),
        )
        return self.c.fetchall()

    def get_game_edges(
        self,
        edge_id=None,
        game=None,
        parent=None,
        child=None,
        edge=None,
        direction=None,
    ):
        """
        Retrieves game edges that satisfy the given constraints
        """
        self.c.execute(
            """
            SELECT * FROM game_edges_table
            WHERE (?1 IS NULL OR edge_id = ?1)
            AND (?2 IS NULL OR game = ?2)
            AND (?3 IS NULL OR parent = ?3)
            AND (?4 IS NULL OR child = ?4)
            AND (?5 IS NULL OR edge = ?5)
            AND (?6 IS NULL OR direction = ?6)
            """,
            (edge_id, game, parent, child, edge, direction),
        )
        return self.c.fetchall()

    def save_single_game(self, graph, edges, creator):
        """
        Saves the state of a created game
        Parameters:
        graph (str): name of the graph being saved
        edges (dictionary of lists): dictionary of lists where the key is an int
            representing the parent and each element in the list is this
            format: {child: <int, index of child in the edge>, type: <str,
            either 'non_neighbor' or 'neighbor'>, edge: <int>, direcion:
            <optional (include if edge is 'neighbor'), str>}
        creator (int): player ID of the creator
        Return value: game ID
        """
        self.c.execute(
            """
            INSERT or IGNORE INTO games_table(graph, creator)
            VALUES (?, ?)
            """,
            (graph, creator),
        )
        game = self.c.lastrowid
        for comp in list(edges.keys()):
            assert self.get_id(id=comp, expand=False)[0][1] in [
                "object",
                "character",
                "room",
            ]
            self.c.execute(
                """
                INSERT or IGNORE INTO game_components_table(game, component)
                VALUES (?, ?)
                """,
                (game, comp),
            )
            for e in edges[comp]:
                child = e["child"]
                assert self.get_id(id=child, expand=False)[0][1] in [
                    "object",
                    "character",
                    "room",
                ]
                if e["type"] == "non_neighbor":
                    self.c.execute(
                        """
                        INSERT or IGNORE INTO game_components_table(game, component)
                        VALUES (?, ?)
                        """,
                        (game, child),
                    )
                    self.c.execute(
                        """
                        INSERT or IGNORE INTO game_edges_table(game, parent, child, edge)
                        VALUES (?, ?, ?, ?)
                        """,
                        (game, comp, child, e["edge"]),
                    )
                elif e["type"] == "neighbor":
                    self.c.execute(
                        """
                        INSERT or IGNORE INTO game_edges_table(game, parent, child, edge, direction)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (game, comp, child, e["edge"], e["direction"]),
                    )
                else:
                    raise Exception("Edge type is unrecognized")
        return game

    def create_triggers(self):
        """
        Creates triggers to keep full text index up to date with the content
        table
        """
        "interaction", "utterance", "participant",
        "turn"
        trigger_info = [
            ("base_objects", ["name"]),
            ("objects", ["name", "physical_description"]),
            ("base_rooms", ["name"]),
            ("rooms", ["name", "description", "backstory"]),
            ("base_characters", ["name"]),
            ("characters", ["name", "persona", "physical_description"]),
            ("utterances", ["dialogue"]),
            ("turns", ["interaction_type", "action"]),
        ]
        for i in trigger_info:
            comma_separated = ", ".join([str(j) for j in i[1]])
            comma_separated_with_new = ", ".join(["new." + str(j) for j in i[1]])
            # can use .format because all variables are defined in the
            # trigger_info table above and cannot be altered by users
            self.c.execute(
                """
                CREATE TRIGGER IF NOT EXISTS {0}_table_bu
                BEFORE UPDATE ON {0}_table
                BEGIN DELETE FROM {0}_table_fts WHERE docid=old.rowid;
                END;
                """.format(
                    i[0]
                )
            )
            self.c.execute(
                """
                CREATE TRIGGER IF NOT EXISTS {0}_table_bd
                BEFORE DELETE ON {0}_table
                BEGIN DELETE FROM {0}_table_fts WHERE docid=old.rowid;
                END;
                """.format(
                    i[0]
                )
            )
            self.c.execute(
                """
                CREATE TRIGGER IF NOT EXISTS {0}_table_bd_au
                AFTER UPDATE ON {0}_table
                BEGIN INSERT INTO {0}_table_fts(docid, {1})
                VALUES(new.rowid, {2});
                END;
                """.format(
                    i[0], comma_separated, comma_separated_with_new
                )
            )
            self.c.execute(
                """
                CREATE TRIGGER IF NOT EXISTS {0}_table_bd_ad
                AFTER INSERT ON {0}_table
                BEGIN INSERT INTO {0}_table_fts(docid, {1})
                VALUES(new.rowid, {2});
                END;
                """.format(
                    i[0], comma_separated, comma_separated_with_new
                )
            )

    def check_custom_tags_objects_tables(self):
        """
        Check if the tables has the attrs related to the custom tagged attributes. If not, add them.
        """

        # Check the table for size column and add if nonexistent
        has_size_column = self.c.execute(
            """
            SELECT COUNT(*) AS CNTREC FROM pragma_table_info('objects_table') WHERE name='size'
            """
        )

        if not has_size_column:
            self.c.execute(
                """
                ALTER TABLE objects_table ADD COLUMN size;
                """
            )

        # Check the table for contain_size column and add if nonexistent
        has_contain_size_column = self.c.execute(
            """
            SELECT COUNT(*) AS CNTREC FROM pragma_table_info('objects_table') WHERE name='contain_size'
            """
        )
        if not has_contain_size_column:
            self.c.execute(
                """
                ALTER TABLE objects_table ADD COLUMN contain_size;
                """
            )

        # Check the table for shape column and add if nonexistent
        has_shape_column = self.c.execute(
            """
            SELECT COUNT(*) AS CNTREC FROM pragma_table_info('objects_table') WHERE name='shape'
            """
        )
        if not has_shape_column:
            self.c.execute(
                """
                ALTER TABLE objects_table ADD COLUMN shape;
                """
            )

        # Check the table for value column and add if nonexistent
        has_value_column = self.c.execute(
            """
            SELECT COUNT(*) AS CNTREC FROM pragma_table_info('objects_table') WHERE name='value'
            """
        )
        if not has_value_column:
            self.c.execute(
                """
                ALTER TABLE objects_table ADD COLUMN value;
                """
            )

    def add_single_conversation(self, room, participants, turns):
        """
        Adds a single conversation to the database
        Parameters:
        room (int): ID of the room the conversation took place in
        participants (list of tuples): list of participants in the format
            (character_id, player_id)
        turns (list of dictionaries): list of turns in the format: {speaker:
            <int, index of speaker in participants list>, listener: <int, index
            of listener in participants list> or None, interaction: {type:
            <text, can be 'speech', 'action', or 'emote'>,
            content: <text>}, turn_time: <int>}
        Return value: interaction_id
        """
        # check if the conversation has already been loaded
        data = []
        for t in turns:
            if t["interaction"]["type"] == "speech":
                data.append(
                    {
                        "speaker": participants[t["speaker"]][0],
                        "text": t["interaction"]["content"],
                    }
                )
        if not self.is_duplicate_conversation(data, room):
            interaction_id = self.create_interaction(room)[0]
            pars = []
            for p in participants:
                pars.append(self.create_participant(interaction_id, p[0], p[1])[0])
            for i, t in enumerate(turns):
                utterance_id = None
                action = None
                if t["interaction"]["type"] == "speech":
                    utterance_id = self.create_utterance(t["interaction"]["content"])[0]
                else:
                    action = t["interaction"]["content"]
                assert t["speaker"] is not None, "Speaker cannot be null"
                if not t["listener"]:
                    self.create_turn(
                        interaction_id,
                        i,
                        t["turn_time"],
                        t["interaction"]["type"],
                        utterance_id,
                        action,
                        pars[t["speaker"]],
                        None,
                    )
                else:
                    self.create_turn(
                        interaction_id,
                        i,
                        t["turn_time"],
                        t["interaction"]["type"],
                        utterance_id,
                        action,
                        pars[t["speaker"]],
                        pars[t["listener"]],
                    )
            return interaction_id
        return -1

    def name_to_id(self, name_to_persona):
        """
        Takes a dictionary mapping between character name and character persona
        and returns a dictionary mapping between character name and character
        id that corresponds to the given persona
        """
        char_dict = {}
        for name in list(name_to_persona.keys()):
            self.c.execute(
                """
                SELECT id from characters_table
                WHERE persona = ?
                """,
                (name_to_persona[name],),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            char_id = int(result[0][0])
            char_dict[name] = char_id
        return char_dict

    def is_duplicate_conversation(self, data, room_id):
        """
        Checks if the conversation has already been loaded. Returns True if
        this conversation already exists in the database and False otherwise.
        """
        possible_interaction_ids = None
        for d in data:
            utterance_id = self.create_utterance(
                d["text"],
                entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
            )[0]
            # For every existing interaction that contains utterance_id, check
            # if the interaction has the same speaker and if it is spoken in
            # the same room. If true, save all the interaction IDs that satisfy
            # these conditions.
            self.c.execute(
                """
                SELECT interaction_id FROM turns_table
                WHERE turns_table.utterance_id = ?
                AND turns_table.interaction_id in (
                    SELECT interaction_id FROM participants_table
                    INNER JOIN interactions_table
                    on interactions_table.id = \
                        participants_table.interaction_id
                    WHERE interactions_table.setting_id = ?
                    AND participants_table.character_id = ?
                )
                """,
                (utterance_id, room_id, d["speaker"]),
            )
            interaction_fetch_result = self.c.fetchall()
            # if this utterance has not been said by this speaker in this room,
            # then this is not a duplicate conversation
            if str(interaction_fetch_result) == "[]":
                return False
            # if possible_interaction_ids is None, then this is the first time
            # executing this for loop.
            elif not possible_interaction_ids:
                possible_interaction_ids = [i[0] for i in interaction_fetch_result]
            # see if any interactions that satisfy the current utterance
            # constraints also satisfy all previous ones. If so, save
            # those for the next comparison
            else:
                current_possible_interaction_ids = [
                    i[0] for i in interaction_fetch_result
                ]
                possible_interaction_ids = list(
                    set(current_possible_interaction_ids)
                    & set(possible_interaction_ids)
                )
            # if there is no interaction that contains all previous utterances
            # with the correct speaker and room, then this conversation does
            # not exist in the database
            if not possible_interaction_ids:
                return False
        return True

    def add_conversation_data(self, pklpath, disable_TQDM=False):
        """
        Loads all conversation data from pickle file located at pklpath.
        """
        conv_parser = ConversationCheckpointParser(pklpath)
        convs_data = conv_parser.get_convs_data()
        for i in tqdm(
            range(len(convs_data)), desc="loading conversations", disable=disable_TQDM
        ):
            room_pickle_id, data = convs_data[i]
            room_id = self.id_room_dict[room_pickle_id]
            # dictionary that maps between character name and character id
            # in the database
            name_to_id = self.name_to_id(conv_parser.name_to_persona(i))
            # if the conversation has not already been added, add it to the
            # database
            for i in data:
                i["speaker"] = name_to_id[i["speaker"]]
                if i["listener"]:
                    i["listener"] = name_to_id[i["listener"]]
            if not self.is_duplicate_conversation(data, room_id):
                interaction_id = self.create_interaction(
                    room_id,
                    entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
                )[0]
                # char_to_participant maps speaker id to (participant ID of
                # speaker, participant ID of listener). Participant ID of
                # listener is None when the speaker is speaking to the room
                char_to_participant = {}
                char1_player_id = self.create_player(
                    entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD}
                )[0]
                char1_id = self.create_participant(
                    interaction_id,
                    data[0]["speaker"],
                    char1_player_id,
                    entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
                )[0]
                if data[0]["listener"] == None:
                    char2_id = None
                    char_to_participant[data[0]["speaker"]] = (char1_id, None)
                else:
                    char2_player_id = self.create_player(
                        entry_attributes={
                            "is_from_pickle": True,
                            "status": DB_STATUS_PROD,
                        }
                    )[0]
                    char2_id = self.create_participant(
                        interaction_id,
                        data[0]["listener"],
                        char2_player_id,
                        entry_attributes={
                            "is_from_pickle": True,
                            "status": DB_STATUS_PROD,
                        },
                    )[0]
                    char_to_participant[data[0]["speaker"]] = (char1_id, char2_id)
                    char_to_participant[data[0]["listener"]] = (char2_id, char1_id)
                turn_number = 0
                # add each turn in order
                for d in data:
                    speaker_id, listener_id = char_to_participant[d["speaker"]]
                    utterance_id = self.create_utterance(
                        d["text"],
                        entry_attributes={
                            "is_from_pickle": True,
                            "status": DB_STATUS_PROD,
                        },
                    )[0]
                    # add turn related to speech
                    self.create_turn(
                        interaction_id,
                        turn_number,
                        d["duration"],
                        "speech",
                        utterance_id,
                        None,
                        speaker_id,
                        listener_id,
                        entry_attributes={
                            "is_from_pickle": True,
                            "status": DB_STATUS_PROD,
                        },
                    )
                    turn_number += 1
                    # add turn related to action/emote, if there are any
                    if d["action"] != None:
                        self.create_turn(
                            interaction_id,
                            turn_number,
                            d["duration"],
                            d["action"][0],
                            None,
                            d["action"][1],
                            speaker_id,
                            listener_id,
                            entry_attributes={
                                "is_from_pickle": True,
                                "status": DB_STATUS_PROD,
                            },
                        )
                        turn_number += 1

    def add_environment_data(self, pklpath, disable_TQDM=False):
        """
        Loads all contents of the pickle file located at pklpath to the database
        """
        enviro_parser = EnvironmentCheckpointParser(pklpath)
        rooms = enviro_parser.get_rooms()
        characters = enviro_parser.get_characters()
        objects = enviro_parser.get_objects()
        neighbors = enviro_parser.get_neighbors()
        # add all rooms
        for i in tqdm(
            range(len(list(rooms.keys()))), desc="loading rooms", disable=disable_TQDM
        ):
            key = list(rooms.keys())[i]
            r = rooms[key]
            base_id = self.create_base_room(
                r["category"],
                entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
            )[0]
            id = self.create_room(
                r["setting"],
                base_id,
                r["description"],
                r["background"],
                entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
            )[0]
            split = "test"
            self.update_split(id, split)
            self.id_room_dict[r["room_id"]] = id
        # add all characters
        for i in tqdm(
            range(len(list(characters.keys()))),
            desc="loading characters",
            disable=disable_TQDM,
        ):
            key = list(characters.keys())[i]
            c = characters[key]
            base_form = min(c["base_form"], key=len).lower()
            base_id = self.create_base_character(
                base_form,
                entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
            )[0]
            # each character can have multiple personas and thus correspond to
            # multiple entries in the database. Each character id in the pickle
            # file corresponds to an array of character ids in the database
            self.id_char_dict[c["character_id"]] = []
            for i in range(len(c["personas"])):
                id = self.create_character(
                    c["name"],
                    base_id,
                    c["personas"][i],
                    c["desc"],
                    entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
                    is_plural=c.get("is_plural"),
                    char_type=c.get("char_type"),
                    name_prefix=c.get("name_prefix"),
                )[0]
                self.id_char_dict[c["character_id"]].append(id)
        # add all objects
        for i in tqdm(
            range(len(list(objects.keys()))),
            desc="loading objects",
            disable=disable_TQDM,
        ):
            key = list(objects.keys())[i]
            o = objects[key]
            base_form = min(o["base_form"], key=len).lower()
            base_id = self.create_base_object(
                base_form,
                entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
            )[0]
            id = self.create_object(
                o["name"],
                base_id,
                o["is_container"],
                o["is_drink"],
                o["is_food"],
                o["is_gettable"],
                o["is_surface"],
                o["is_wearable"],
                o["is_weapon"],
                o["descriptions"][0],
                entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
                name_prefix=o.get("name_prefix"),
                is_plural=o.get("is_plural"),
            )[0]
            self.id_object_dict[o["object_id"]] = id
        # add all node content (edges)
        # in corresponds to inside the description and ex corresponds to
        # extra possibility. In has edge strength 1 and ex has edge strength 0
        for i in tqdm(
            range(len(list(rooms.keys()))),
            desc="loading edges for rooms",
            disable=disable_TQDM,
        ):
            key = list(rooms.keys())[i]
            r = rooms[key]
            for i in r["ex_characters"]:
                char_lst = self.id_char_dict[i]
                for c in char_lst:
                    self.create_node_content(
                        self.id_room_dict[r["room_id"]],
                        c,
                        "ex_contained",
                        0,
                        entry_attributes={
                            "is_from_pickle": True,
                            "status": DB_STATUS_PROD,
                        },
                    )
            for i in r["ex_objects"]:
                self.create_node_content(
                    self.id_room_dict[r["room_id"]],
                    self.id_object_dict[i],
                    "ex_contained",
                    0,
                    entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
                )
            for i in r["in_characters"]:
                char_lst = self.id_char_dict[i]
                for c in char_lst:
                    self.create_node_content(
                        self.id_room_dict[r["room_id"]],
                        c,
                        "in_contained",
                        1,
                        entry_attributes={
                            "is_from_pickle": True,
                            "status": DB_STATUS_PROD,
                        },
                    )
            for i in r["in_objects"]:
                self.create_node_content(
                    self.id_room_dict[r["room_id"]],
                    self.id_object_dict[i],
                    "in_contained",
                    1,
                    entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
                )
        for i in tqdm(
            range(len(list(characters.keys()))),
            desc="loading edges for characters",
            disable=disable_TQDM,
        ):
            key = list(characters.keys())[i]
            c = characters[key]
            char_lst = self.id_char_dict[c["character_id"]]
            for i in c["wearing_objects"]:
                for char in char_lst:
                    if type(i) is str:
                        self.create_text_edge(
                            char,
                            str(i),
                            DB_EDGE_WORN,
                            1,
                            entry_attributes={
                                "is_from_pickle": True,
                                "status": DB_STATUS_PROD,
                            },
                        )
                    else:
                        self.create_node_content(
                            char,
                            self.id_object_dict[i],
                            DB_EDGE_WORN,
                            1,
                            entry_attributes={
                                "is_from_pickle": True,
                                "status": DB_STATUS_PROD,
                            },
                        )
            for i in c["wielding_objects"]:
                for char in char_lst:
                    if type(i) is str:
                        self.create_text_edge(
                            char,
                            str(i),
                            DB_EDGE_WIELDED,
                            1,
                            entry_attributes={
                                "is_from_pickle": True,
                                "status": DB_STATUS_PROD,
                            },
                        )
                    else:
                        self.create_node_content(
                            char,
                            self.id_object_dict[i],
                            DB_EDGE_WIELDED,
                            1,
                            entry_attributes={
                                "is_from_pickle": True,
                                "status": DB_STATUS_PROD,
                            },
                        )
            for i in c["carrying_objects"]:
                for char in char_lst:
                    if type(i) is str:
                        self.create_text_edge(
                            char,
                            str(i),
                            DB_EDGE_IN_CONTAINED,
                            1,
                            entry_attributes={
                                "is_from_pickle": True,
                                "status": DB_STATUS_PROD,
                            },
                        )
                    else:
                        self.create_node_content(
                            char,
                            self.id_object_dict[i],
                            DB_EDGE_IN_CONTAINED,
                            1,
                            entry_attributes={
                                "is_from_pickle": True,
                                "status": DB_STATUS_PROD,
                            },
                        )
        # add neighbors for rooms
        for i in tqdm(
            range(len(neighbors)), desc="loading neighbors", disable=disable_TQDM
        ):
            id, n_dict = neighbors[i]
            # We read the destination, direction, and direction from the neighbor in
            # as the child_text, child_label, and child_desc respectively.
            child_text = n_dict["destination"]
            child_label = n_dict["direction"]
            child_desc = n_dict["connection"]

            # create text edge with edge type "neighbor" and edge strength 1
            # -1 indicates there is no parent room
            if id == -1:
                continue
                # TODO we may have to handle these separately somehow.
                self.create_text_edge(
                    None,
                    child_text,
                    DB_EDGE_NEIGHBOR,
                    1,
                    child_label=child_label,
                    child_desc=child_desc,
                    entry_attributes={"is_from_pickle": True, "status": DB_STATUS_PROD},
                )
            else:
                # some rooms in the original data are rejected and thus don't
                # have corresponding entries in the database
                try:
                    self.create_text_edge(
                        self.id_room_dict[id],
                        child_text,
                        DB_EDGE_NEIGHBOR,
                        1,
                        child_label=child_label,
                        child_desc=child_desc,
                        entry_attributes={
                            "is_from_pickle": True,
                            "status": DB_STATUS_PROD,
                        },
                    )
                except KeyError:
                    pass

    def get_table_name(self, id, return_type=False):
        """
        Returns the name of the table that the given ID belongs to
        """
        self.c.execute("SELECT type FROM id_table WHERE id = ?", (id,))
        name = self.c.fetchall()
        # Check if ID is present in the database
        assert str(name) != "[]", "ID does not exist"
        type = str(name[0][0])
        table_name = self.table_dict[type]
        if return_type:
            return type
        else:
            return table_name

    def get_query(self, id):
        """
        Given a generic id in the id_table, locate the correct table and
        return the results for the query.
        """
        table_name = self.get_table_name(id)
        # Can use .format because table_name is being chosen from a predefined
        # list, so there is no risk for SQL injection
        self.c.execute(
            """
            SELECT * FROM {}
            WHERE id = ?
            """.format(
                table_name
            ),
            (id,),
        )
        # there should only be one matching entry
        result = self.c.fetchall()
        assert len(result) == 1
        return result[0]

    def init_edits_table(self):
        # Table to keep track of potential edits
        self.c.execute(
            """
              CREATE TABLE IF NOT EXISTS edits_table (
              edit_id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
              id integer NOT NULL,
              field text NOT NULL,
              unedited_value text,
              edited_value text,
              player_id integer NOT NULL,
              status text NOT NULL DEFAULT '{}',
              UNIQUE (id, field, unedited_value, edited_value),
              CONSTRAINT fk_id FOREIGN KEY (id)
                  REFERENCES id_table (id)
                  ON DELETE CASCADE,
              CONSTRAINT fk_status FOREIGN KEY (status)
                  REFERENCES enum_table_status (status)
                  ON DELETE CASCADE);
              """.format(
                DB_STATUS_REVIEW
            )
        )

    def submit_edit(self, id, field, edit, player_id):
        """
        Parameters:
        id (int): ID of the entry to be edited
        field (string): Column name
        edit (string): Proposed edit
        """
        result = self.get_query(id)
        # check if field is present in the entry
        column_names = list(map(lambda x: x[0], self.c.description))
        table_name = self.get_table_name(id)
        assert (
            field in column_names
        ), "Field is not present in the selected \
            entry"
        # if utterance is edited, change edit field to utterance ID instead of
        # raw text Note that a new entry in the utterance table is created if
        # the utternace is not already in the database
        if field == "utterance_id":
            edit = self.create_utterance(edit)[0]
        # get the unedited text
        self.c.execute(
            """
            SELECT {} FROM {} WHERE id = ?
            """.format(
                field, table_name
            ),
            (id,),
        )
        result = self.c.fetchall()
        assert len(result) == 1
        unedited = result[0][0]
        # insert into edits_table
        self.c.execute(
            """
            INSERT OR IGNORE INTO edits_table (id, field, unedited_value, \
            edited_value, player_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (id, field, unedited, edit, player_id),
        )
        return self.c.lastrowid

    def get_edit(
        self,
        edit_id=None,
        id=None,
        field=None,
        unedited_value=None,
        edited_value=None,
        player_id=None,
        status=None,
    ):
        """
        Retrieves edits that satisfy the given constraints
        """
        self.c.execute(
            """
            SELECT * FROM edits_table
            WHERE (?1 IS NULL OR edit_id = ?1)
            AND (?2 IS NULL OR id = ?2)
            AND (?3 IS NULL OR field = ?3)
            AND (?4 IS NULL OR unedited_value = ?4)
            AND (?5 IS NULL OR edited_value = ?5)
            AND (?6 IS NULL OR player_id = ?6)
            AND (?7 IS NULL OR status = ?7)
            """,
            (edit_id, id, field, unedited_value, edited_value, player_id, status),
        )
        return self.c.fetchall()

    def enact_edit(self, edit_id):
        """
        Used to enact all edits except ones related to utterances
        """
        # table_name and field is checked so there is no risk for SQL injection
        # by using .format
        self.c.execute(
            """
            SELECT id, field, edited_value FROM edits_table
            WHERE edit_id = ?
            """,
            (edit_id,),
        )
        (id, field, edit) = self.c.fetchall()[0]
        table_name = self.get_table_name(id)
        self.c.execute(
            """
            UPDATE {}
            SET {} = ?
            WHERE id = ?;
            """.format(
                table_name, field
            ),
            (edit, id),
        )

    def enact_edit_utterance(self, edit_id):
        """
        Edits the database when an utterance is marked for editing. Copies the
        conversation except the single edited utterance
        """
        # get information about the edited utterance and turn from edited_id
        self.c.execute(
            """
            SELECT id, field, unedited_value, edited_value, status
            FROM edits_table WHERE edit_id = ?
            """,
            (edit_id,),
        )
        (id, field, unedited, edit, status) = self.c.fetchall()[0]
        self.c.execute(
            """
            SELECT id, field, unedited_value, edited_value
            FROM edits_table WHERE edit_id = ?
            """,
            (edit_id,),
        )
        (id, field, unedited, edit) = self.c.fetchall()[0]
        if status == DB_STATUS_ACCEPT_ALL:
            # get all interactions that contain the utterance
            self.c.execute(
                """
                SELECT interaction_id FROM turns_table
                WHERE utterance_id = ?
                """,
                (unedited,),
            )
            result = self.c.fetchall()
            # get rid of potential duplicate interaction IDs (occurs when the
            # utterance marked for editing appears twice in a conversation)
            interaction_ids = list(set([i[0] for i in result]))
        elif status == DB_STATUS_ACCEPT_ONE:
            # only consider the interaction that is marked for editing
            interaction_ids = [self.get_query(id)[1]]
        else:
            # should not end up here
            raise Exception("Status error in edits_table")
        # Replicate all interactions with edited turn
        for i in interaction_ids:
            setting_id = self.get_interaction(id=i)[0][1]
            interaction_id = self.create_interaction(setting_id)[0]
            turns = self.get_turn(interaction_id=i)
            for turn in turns:
                (
                    current_id,
                    _,
                    turn_number,
                    turn_time,
                    interaction_type,
                    utterance_id,
                    action,
                    speaker_id,
                    listener_id,
                ) = turn
                if (status == DB_STATUS_ACCEPT_ONE) and (current_id == id):
                    # add turn with edited content when encountering the turn with
                    # utterance_id marked for editing
                    self.create_turn(
                        interaction_id,
                        turn_number,
                        turn_time,
                        interaction_type,
                        edit,
                        action,
                        speaker_id,
                        listener_id,
                    )
                elif (status == DB_STATUS_ACCEPT_ALL) and (
                    utterance_id == int(unedited)
                ):
                    self.create_turn(
                        interaction_id,
                        turn_number,
                        turn_time,
                        interaction_type,
                        edit,
                        action,
                        speaker_id,
                        listener_id,
                    )
                # for all other turns, replicate them
                else:
                    self.create_turn(
                        interaction_id,
                        turn_number,
                        turn_time,
                        interaction_type,
                        utterance_id,
                        action,
                        speaker_id,
                        listener_id,
                    )

    def view_edit(self, edit_id):
        """
        Returns context necessary to review an edit in dictionary form
        """
        assert len(self.get_edit(edit_id=edit_id)) == 1, "Edit doees not exist"
        (
            edit_id,
            id,
            field,
            unedited_value,
            edited_value,
            player_id,
            status,
        ) = self.get_edit(edit_id=edit_id)[0]
        edit_column_names = list(map(lambda x: x[0], self.c.description))
        edit_row = self.get_edit(edit_id=edit_id)[0]
        entity_values = self.get_query(edit_row["id"])
        # result now contains all information from the edits_table about a
        # particular edit in dictionary form
        result = {key: edit_row[key] for key in edit_column_names}
        # include the type of entity being edited
        assert len(self.get_id(id=id)) == 1, "ID does not exist"
        result["type"] = self.get_id(id=id)[0][1]
        # if base form exists, then include it in the dictionary
        if self.get_id(id=id)[0][1] in ["object", "character", "room"]:
            base_index = 2
            result["base"] = self.get_query(entity_values["base_id"])[1]
        # if the entity being edited is utterance, then include additional
        # information: all other utterances in the conversation, room ID, and
        # characters involved
        elif field == "utterance_id":
            interaction_id = entity_values[1]
            # set type of result as utterance
            result["type"] = "utterance"
            # get all turns in the interaction
            turns = self.get_turn(interaction_id=interaction_id)
            # get all utterances from the turns
            utterance_index = 5
            result["utterances"] = [
                self.get_utterance(id=i[utterance_index])[0][1] for i in turns
            ]
            # get room name
            room_id = self.get_query(interaction_id)[1]
            assert len(self.get_room(id=room_id)) == 1, "Room ID is not valid"
            result["room"] = self.get_room(id=room_id)[0][1]
            # get character names
            # If there are two characters, the first character in the
            # result['characters'] list is the first character to speak.
            # If there is one character, there is only one element in the list
            participant_ids = [turns[0][-2], turns[0][-1]]
            participant_ids = [i for i in participant_ids if i is not None]
            assert all(
                len(self.get_participant(id=i)) == 1 for i in participant_ids
            ), "Participant ID is not valid"
            char_ids = [self.get_participant(id=i)[0][2] for i in participant_ids]
            assert all(
                len(self.get_character(id=i)) == 1 for i in char_ids
            ), "Character ID is not valid"
            result["characters"] = [self.get_character(id=i)[0][1] for i in char_ids]
            # get the value that the utterance is being edited to
            assert (
                len(self.get_utterance(id=result["edited_value"])) == 1
            ), "Utterance ID is not valid"
            result["edited_value"] = self.get_utterance(id=result["edited_value"])[0][1]
            # turn number can be used to determine the original utterance
            # marked for editing (don't use utterance_id or utterance text
            # because that will not uniquely determine the utterance being
            # edited if an utterance is repeated in the same conversation)
            result["turn_number"] = entity_values[2]
            # utterance ID is not necessary
            result.pop("unedited_value")
        return result

    def accept_edit(self, edit_id, accept_type):
        """
        Parameters:
        edit_id (int): Primary key of edit in the edits_table
        accept_type (string):
            accept: used for all entries except edits to utterances
            accept_one: accept edit for utterance in one location
            accept_all: accept edit for all appearances of the utterance

        Changes status in the edit table and edits the database
        """
        self.c.execute(
            """
            UPDATE edits_table
            SET status = ?
            WHERE edit_id = ?
            """,
            (accept_type, edit_id),
        )
        if accept_type == "accepted":
            self.enact_edit(edit_id)
        else:
            self.enact_edit_utterance(edit_id)

    def reject_edit(self, edit_id):
        """
        Marks edit as rejected in the edits_table
        """
        self.c.execute(
            """
            UPDATE edits_table
            SET status = 'rejected'
            WHERE edit_id = ?
            """,
            (edit_id,),
        )

    def find_entities_in_rooms(self, room, chars, objs):
        """
        Find characters and objects in chars and objs that should be a part of
        a room. Helper function for create_edges
        """
        room_desc = self.get_query(room)[3]
        in_contained_chars = []
        in_contained_objs = []
        for char in chars:
            if self.get_query(char)[1] in room_desc:
                in_contained_chars.append(char)
        for obj in objs:
            if self.get_query(obj)[1] in room_desc:
                in_contained_objs.append(obj)
        return in_contained_chars, in_contained_objs

    def find_database_entities_in_rooms(self, room):
        """
        Given a room, find all objects/characters in the database that have names
        entirely contained in the room description.
        """
        room_desc = self.get_query(room)[3]
        self.c.execute(
            """
            SELECT * FROM characters_table
            WHERE INSTR(?, name) > 0
            """,
            (room_desc,),
        )
        characters = self.c.fetchall()
        self.c.execute(
            """
            SELECT * FROM objects_table
            WHERE INSTR(?, name) > 0
            """,
            (room_desc,),
        )
        objects = self.c.fetchall()
        dict = defaultdict(list)
        for i in characters + objects:
            dict[i[1]].append(i[0])
        results = [random.choice(lst) for lst in list(dict.values())]
        return results

    def create_edges(self, room, chars, objs, rooms, dry_run):
        """Called when creating new entities"""
        edges_lst = []
        in_contained_chars, in_contained_objs = self.find_entities_in_rooms(
            room, chars, objs
        )
        for i in in_contained_chars + in_contained_objs:
            edges_lst.append((room, i, DB_EDGE_IN_CONTAINED, 1))
        for char in list(set(chars) - set(in_contained_chars)):
            edges_lst.append((room, char, DB_EDGE_EX_CONTAINED, 0))
        for obj in list(set(objs) - set(in_contained_objs)):
            edges_lst.append((room, obj, DB_EDGE_EX_CONTAINED, 0))
        for r in rooms:
            edges_lst.append((room, r, DB_EDGE_NEIGHBOR, 1))
        if not dry_run:
            for i in edges_lst:
                self.create_node_content(*i)
        return edges_lst

    # -------------------Database added for WorldBuilder-------------#
    def set_autosave(self, world_dump, player_id, timestamp):
        # Existing autosave?
        self.c.execute(
            """
            SELECT * FROM auto_save_table
            WHERE owner_id = ?
            """,
            (player_id,),
        )
        if len(self.c.fetchall()) == 1:
            # Existing then update
            self.c.execute(
                """
                UPDATE auto_save_table
                SET timestamp = ?, world_dump = ?
                WHERE owner_id = ?;
                """,
                (timestamp, world_dump, player_id,),
            )
        else:
            # Otherwise, just insert
            self.c.execute(
                """
                INSERT or IGNORE INTO auto_save_table(owner_id, timestamp, world_dump)
                VALUES (?, ?, ?)
                """,
                (player_id, timestamp, world_dump,),
            )

    def get_autosave(self, player_id):
        # Get existing autosave
        self.c.execute(
            """
            SELECT * FROM auto_save_table
            WHERE owner_id = ?
            """,
            (player_id,),
        )
        return self.c.fetchone()

    def get_active_worlds_owned_by(self, player_id):
        """
        Return a list of all worlds owned by the player which are active
        """
        self.c.execute(
            """
            SELECT * FROM world_table
            WHERE owner_id = ? and in_use = 1;
            """,
            (player_id,),
        )
        return self.c.fetchall()

    def is_world_owned_by(self, world_id, player_id):
        self.c.execute(
            """
            SELECT * FROM world_table
            WHERE id = ? AND owner_id = ?
            """,
            (world_id, player_id),
        )
        return len(self.c.fetchall()) == 1

    def get_world(self, world_id, player_id):
        """
        Return the data for a world given its ID
        """
        assert self.is_world_owned_by(
            world_id, player_id
        ), "Cannot load a world you do not own"
        if self.use_cache:
            if world_id is not None and world_id in self.cache["worlds"]:
                return [self.cache["worlds"][world_id]]
        self.c.execute(
            """
            SELECT * FROM world_table
            WHERE id = ? AND owner_id = ?
            """,
            (world_id, player_id,),
        )
        return self.c.fetchall()

    def set_world_inactive(self, world_id, player_id):
        """
            Makes a world in the world table inactive if owned by player_id
        """
        assert self.is_world_owned_by(
            world_id, player_id
        ), "Cannot change a world you do not own"
        self.c.execute(
            """
            UPDATE world_table
            SET in_use = 0
            WHERE id = ?;
            """,
            (world_id,),
        )
        if self.use_cache and world_id in self.cache["worlds"]:
            self.c.execute("""SELECT * FROM world_table WHERE id = ? """, (world_id,))
            self.cache["worlds"][world_id] = self.c.fetchone()

    def get_world_resources(self, world_id, player_id):
        assert self.is_world_owned_by(
            world_id, player_id
        ), "Cannot load a world you do not own"

        # Get tiles tied to this world
        self.c.execute(
            """
            SELECT * FROM tile_table
            WHERE world_id = ?
            """,
            (world_id,),
        )
        tiles = self.c.fetchall()

        # Get edges tied to this world
        self.c.execute(
            """
            SELECT * FROM edges_table
            WHERE w_id = ?
            """,
            (world_id,),
        )
        edges = self.c.fetchall()

        # Get rooms joined with room nodes associated with this world
        self.c.execute(
            """
            SELECT * FROM nodes_table INNER JOIN rooms_table ON nodes_table.entity_id=rooms_table.id
            WHERE w_id = ?
            """,
            (world_id,),
        )
        room_nodes = self.c.fetchall()

        # Get characters joined with character nodes associated with this world
        self.c.execute(
            """
            SELECT * FROM nodes_table INNER JOIN characters_table ON nodes_table.entity_id=characters_table.id
            WHERE w_id = ?
            """,
            (world_id,),
        )
        character_nodes = self.c.fetchall()

        # Get objects joined with object nodes associated with this world
        self.c.execute(
            """
            SELECT * FROM nodes_table INNER JOIN objects_table ON nodes_table.entity_id=objects_table.id
            WHERE w_id = ?
            """,
            (world_id,),
        )
        object_nodes = self.c.fetchall()

        return [tiles, edges, room_nodes, character_nodes, object_nodes]

    def delete_world(self, world_id, player_id):
        """
        Delete the world data for a world given its ID
        """
        assert self.is_world_owned_by(
            world_id, player_id
        ), "Cannot delete a world you do not own"
        self.delete_id(world_id)
        return world_id

    def view_worlds(self, player_id):
        """
        Format world names and ids owned by the player for viewing
        """
        player_worlds = self.get_active_worlds_owned_by(player_id=player_id)
        res = [dict(row) for row in player_worlds]
        return res

    def get_num_worlds_owned_by(self, player_id):
        """
        Return the number of worlds owned by a user
        """
        return len(self.get_active_worlds_owned_by(player_id))

    def get_edge(self, world_id, edge_id):
        self.c.execute(
            """
            SELECT src_id, dst_id, edge_type FROM edges_table
            WHERE id = ? AND w_id = ?
            """,
            (edge_id, world_id,),
        )
        return self.c.fetchall()

    # Should return all tiles belonging to the world
    def get_tiles(self, world_id):
        self.c.execute(
            """
            SELECT * FROM tile_table
            WHERE world_id = ?
            """,
            (world_id,),
        )
        return self.c.fetchall()

    def get_node(self, node_id):
        self.c.execute(
            """
            SELECT * FROM nodes_table
            WHERE id = ?
            """,
            (node_id,),
        )
        return self.c.fetchall()

    # Gets all connected components to this tile
    def get_edges(self, tile_id, edges):
        self.c.execute(
            """
            SELECT room_node_id FROM tile_table
            WHERE id = ?
            """,
            (tile_id,),
        )
        crit_node_id = self.c.fetchall()[0][0]
        self.get_connected(crit_node_id, edges)

    def get_connected(self, node_id, edges):
        self.c.execute(
            """
            SELECT * FROM edges_table
            WHERE src_id = ?
            """,
            (node_id,),
        )
        edges_connected = self.c.fetchall()
        for e in edges_connected:
            old_len = len(edges)
            edges.add(e)
            if old_len != len(edges):
                self.get_connected(e["dst_id"], edges)

    def create_tile(
        self,
        world_id,
        room_id,
        color,
        x_coordinate,
        y_coordinate,
        floor,
        entry_attributes={},
    ):
        id = self.create_id(DB_TYPE_TILE, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO tile_table(id, world_id, room_node_id,
            color, x_coordinate, y_coordinate, floor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (id, world_id, room_id, color, x_coordinate, y_coordinate, floor,),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from tile_table WHERE world_id = ? AND room_node_id = ? \
                AND color = ? AND x_coordinate = ? AND y_coordinate = ? AND floor = ?
                """,
                (world_id, room_id, color, x_coordinate, y_coordinate, floor),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_graph_node(self, w_id, entity_id, entry_attributes={}):
        id = self.create_id(DB_TYPE_GRAPH_NODE, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO nodes_table(id, w_id, entity_id)
            VALUES (?, ?, ?)
            """,
            (id, w_id, entity_id,),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from nodes_table WHERE w_id = ? AND entity_id = ?
                """,
                (w_id, entity_id,),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_graph_edge(self, w_id, src_id, dst_id, type_, entry_attributes={}):
        id = self.create_id(DB_TYPE_GRAPH_EDGE, entry_attributes)
        self.c.execute(
            """
            INSERT or IGNORE INTO edges_table(id, w_id, src_id, dst_id, edge_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (id, w_id, src_id, dst_id, type_,),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from edges_table WHERE w_id = ? AND src_id = ? AND dst_id = ? \
                AND edge_type = ?
                """,
                (w_id, src_id, dst_id, type_),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_world(
        self,
        name,
        owner_id,
        height,
        width,
        num_floors,
        in_use=True,
        entry_attributes={},
    ):

        LIMIT = 10
        num_worlds = self.get_num_worlds_owned_by(owner_id)
        if num_worlds >= LIMIT:
            return (-1, False)

        id = self.create_id(DB_TYPE_WORLD, entry_attributes)
        in_use = 1 if in_use else 0
        self.c.execute(
            """
            INSERT or IGNORE INTO world_table(id, name, owner_id,
            height, width, num_floors, in_use)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (id, name, owner_id, height, width, num_floors, in_use,),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.delete_id(id)
            self.c.execute(
                """
                SELECT id from world_table WHERE name = ? AND owner_id = ? \
                AND height = ? AND width = ? AND num_floors = ? AND in_use = ?
                """,
                (name, owner_id, height, width, num_floors, in_use),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        return (id, inserted)

    def create_user(self, username):
        self.c.execute(
            """
            INSERT or IGNORE INTO user_table(username)
            VALUES (?)
            """,
            (username,),
        )
        inserted = bool(self.c.rowcount)
        if not inserted:
            self.c.execute(
                """
                SELECT id from user_table WHERE username = ?
                """,
                (username,),
            )
            result = self.c.fetchall()
            assert len(result) == 1
            id = int(result[0][0])
        else:
            id = self.c.lastrowid
        return (id, inserted)

    def get_user_id(self, username):
        self.c.execute(
            """
                SELECT id from user_table WHERE username = ?
                """,
            (username,),
        )
        result = self.c.fetchall()
        assert len(result) == 1
        id = int(result[0][0])
        return id
