#!/usr/bin/env python3

# Copyright 2017-present, Facebook, Inc.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.db.base import BaseDB
from omegaconf import MISSING, DictConfig
from typing import Optional, Union, Dict, Any


DB_STATUS_REVIEW = "unreviewed"
DB_SPLIT_UNSET = "no_set_split"


class EnvDB(BaseDB):
    """
    Environment database for LIGHT, containing accessors for the
    LIGHT environment, nodes, attributes, additional annotations,
    quests, world-interactions, and more.
    """

    def _complete_init(self, config: "DictConfig"):
        """
        Initialize any specific environment-related paths
        """
        raise NotImplementedError()

    def _validate_init(self):
        """
        Ensure that the environment manifest exists, and that key
        paths are properly initialized
        """
        raise NotImplementedError()

    def _first_init_tables(self):
        """If the tables don't exist at all, create them."""

    def create_node_cache(self) -> None:
        """
        Create a local cached version of the environment nodes and
        relationships, to use for rapid construction of things
        without needing repeated queries
        """

    # Agents

    def create_base_agent(self, name: str) -> str:
        """Create a new agent name in the database"""
        # Return base_char_id

    def get_base_agent(
        self, name: Optional[str] = None, id: Optional[str] = None
    ) -> "DBBaseAgent":
        """Get a specific base agent, assert that it exists"""

    def create_agent_entry(
        self,
        name: str,
        persona: str,
        physical_description: str,
        name_prefix: Optional[str] = None,
        is_plural: Optional[str] = None,
        size: Optional[int] = None,
        contain_size: Optional[int] = None,
        constitution: Optional[int] = None,
        charisma: Optional[int] = None,
        strength: Optional[int] = None,
        dexterity: Optional[int] = None,
        intelligence: Optional[int] = None,
        wisdom: Optional[int] = None,
        status: str = DB_STATUS_REVIEW,
        split: str = DB_SPLIT_UNSET,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create this agent, making a base_agent first if required"""
        # Return agent_id

    def find_agents(
        self,
        base_id: Optional[str] = None,
        name: Optional[str] = None,
        persona: Optional[str] = None,
        physical_description: Optional[str] = None,
        name_prefix: Optional[str] = None,
        is_plural: Optional[str] = None,
        status: Optional[str] = None,
        split: Optional[str] = None,
        creator_id: Optional[str] = None,
    ) -> List["DBAgent"]:
        """Return all agents matching the given parameters"""

    def get_agent(self, id: str) -> "DBAgent":
        """Return the given agent, raise an exception if non-existing"""

    # Objects

    def create_base_object(self, name: str) -> str:
        """Create a new object name in the database"""
        # Return base_obj_id

    def get_base_object(
        self, name: Optional[str] = None, id: Optional[str] = None
    ) -> "DBBaseObject":
        """Get a specific base object, assert that it exists"""

    def create_object_entry(
        self,
        name: str,
        physical_description: str,
        is_container: float,
        is_drink: float,
        is_food: float,
        is_gettable: float,
        is_surface: float,
        is_wearable: float,
        is_weapon: float,
        name_prefix: Optional[str] = None,
        is_plural: Optional[str] = None,
        size: Optional[int] = None,
        contain_size: Optional[int] = None,
        value: Optional[float] = None,
        rarity: Optional[float] = None,
        status: str = DB_STATUS_REVIEW,
        split: str = DB_SPLIT_UNSET,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create a new object, making a base_object first if required"""
        # Return object_id

    def find_objects(
        self,
        base_id: Optional[str] = None,
        name: Optional[str] = None,
        physical_description: Optional[str] = None,
        is_container: Optional[bool] = None,
        is_drink: Optional[bool] = None,
        is_food: Optional[bool] = None,
        is_gettable: Optional[bool] = None,
        is_surface: Optional[bool] = None,
        is_wearable: Optional[bool] = None,
        is_weapon: Optional[bool] = None,
        name_prefix: Optional[str] = None,
        is_plural: Optional[str] = None,
        status: Optional[str] = None,
        split: Optional[str] = None,
        creator_id: Optional[str] = None,
    ) -> List["DBObject"]:
        """Return all objects matching the given parameters"""

    def get_object(self, id: str) -> "DBObject":
        """Return the given object, raise exception if non-existing"""

    # Rooms

    def create_base_room(self, name: str) -> str:
        """Create a new room name in the database"""
        # Return base_room_id

    def get_base_room(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> "DBBaseRoom":
        """Return all base rooms matching the given parameters"""

    def create_room_entry(
        self,
        name: str,
        description: str,
        backstory: str,
        size: Optional[int] = None,
        indoor_status: Optional[str] = None,
        rarity: Optional[float] = None,
        status: str = DB_STATUS_REVIEW,
        split: str = DB_SPLIT_UNSET,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create a new room, making a base_room first if required"""
        # Return room_id

    def find_rooms(
        self,
        base_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        backstory: Optional[str] = None,
        indoor_status: Optional[str] = None,
        status: Optional[str] = None,
        split: Optional[str] = None,
        creator_id: Optional[str] = None,
    ) -> List["DBRoom"]:
        """Return all rooms matching the given parameters"""

    def get_room(self, id: str) -> "DBRoom":
        """Get a specific room, assert that it exists"""

    # Attributes

    def create_arbitrary_attribute(
        self,
        target_id: str,
        attribute_name: str,
        attribute_value_string: str,
        status: str = DB_STATUS_REVIEW,
        creator_id: Optional[str] = None,
    ) -> None:
        """Create an arbitrary attribute entry for the target node"""

    # Edges

    def create_edge(
        self,
        parent_id: str,
        child_id: str,
        edge_type: str,
        edge_strength: int = 1,
        status: str = DB_STATUS_REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create an edge between two nodes"""

    def get_edges(
        self,
        parent_id: Optional[str] = None,
        child_id: Optional[str] = None,
        edge_type: Optional[str] = None,
        status: Optional[str] = None,
        creator_id: Optional[str] = None,
    ):
        """Return all edges matching the given parameters"""

    def create_text_edge(
        self,
        parent_id: str,
        child_text: str,
        edge_type: str,
        edge_strength: int = 1,
        status: str = DB_STATUS_REVIEW,
        creator_id: Optional[str] = None,
    ) -> str:
        """Create an edge between a node and the name of a possible leaf"""

    def get_text_edges(
        self,
        parent_id: Optional[str] = None,
        child_text: Optional[str] = None,
        edge_type: Optional[str] = None,
        status: Optional[str] = None,
        creator_id: Optional[str] = None,
    ):
        """Return all text edges matching the given parameters"""

    # Flags and edits

    def create_edit(
        self,
        user_id: str,
        table: str,
        node_id: str,
        field: str,
        value: Any,
    ) -> str:
        """Write a potential edit to file. Return the edit filename"""

    def get_edits(
        self,
        user_id: Optional[str] = None,
        table: Optional[str] = None,
        node_id: Optional[str] = None,
        field: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List["DBEdit"]:
        """Return all edits matching the given parameters"""

    def flag_entry(
        self,
        user_id: str,
        table: str,
        node_id: str,
        reason: str,
    ) -> str:
        """
        Write a potential flag to file, update the node's status,
        return the flag filename
        """

    def get_flags(
        self,
        user_id: str,
        table: str,
        node_id: str,
        status: Optional[str] = None,
    ) -> List["DBFlag"]:
        """Return all flags matching the given parameters"""

    # Quests

    ## TODO Figure out a format for quests/motivations -> target action? Subquests?
    ## motivation text -> desired action outcome, or list of subquests, associated characters

    # Worlds

    ## TODO Figure out the world saving format. Likely just owner+metadata and write to file
