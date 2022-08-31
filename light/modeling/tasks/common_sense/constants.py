# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

from enum import Enum

INST_LIGHT_MSG = (
    "You need to have LIGHT (https://github.com/facebookresearch/LIGHT) installed."
)

try:
    from light.graph.events.all_events_list import (
        GoEvent,
        UnfollowEvent,
        FollowEvent,
        UnblockEvent,
        BlockEvent,
        HelpEvent,
        HitEvent,
        HugEvent,
        GetObjectEvent,
        PutObjectInEvent,
        DropObjectEvent,
        StealObjectEvent,
        GiveObjectEvent,
        EquipObjectEvent,
        WearEvent,
        WieldEvent,
        RemoveObjectEvent,
        IngestEvent,
        EatEvent,
        DrinkEvent,
    )

except ModuleNotFoundError:
    raise ModuleNotFoundError(INST_LIGHT_MSG)

# The local dataset files and pieces
DIALOG_DATASET_FNAME = "light_data.pkl"
DIALOG_DATASET_UNSEEN_FNAME = "light_unseen_data.pkl"
# TODO: ask Jack, is this the same data as we have in DB (just older)?
ENV_DATASET = "light_environment.pkl"
LIGHT_DBNAME = "database3.db"

# The generated files and directories names
DATASET_DIR_NAME = "light_common_sense"
ROOM_CONTENTS_DIR = "rooms_and_contents"
GAMEPLAY_DIR = "gameplays"

# Original source of the LIGHT DB (hopefully up to date)
ORIGINAL_LIGHT_DB_ADDRESS = "/checkpoint/light/data/database3.db"

# LIGHT game play datset
ORIGINAL_LIGHT_GAMEPLAY_PATH = "/private/home/jju/data/light/"
GAMEPLAY_SPLITS = ("train", "valid", "test", "unseen")

MODEL_NAMES = (
    "sludge_all_Wed_Dec__1/0e6",
    "sludge_all_do5_Sat_Dec__4/51f",
    "bart_all_Mon_Nov_15/ce3",
    "bart_all_weighted_Wed_Nov_10/703",
    "bart_allroom_Wed_Nov_10/c09",
    "bart_all_weighted_Thu_Nov_11/58c",
    "sludge_all__Mon_Dec__6/910",
)

# Graph state definition syntax
GRAPH_TUPLES_DELIM = " -=- "
GRAPH_STATES_DELIM = "\n"
GRAPH_STATES_DELIM_HIST = "\t"


class GraphMutations(Enum):
    ADD = 1
    DEL = 2
    NO_MUTATION = 3


# The threshold of the value assigned to a an attribute to consider it having that attribute.
# For example, for `is_drinkable` attribute, values more than this threshold means the object
# is drinkable, and vice versa.
ATTRIBUTE_VALUE_THRESHOLD = 0.1


class GraphEdges(Enum):
    IS_TYPE = 1
    IS_INSIDE = 2
    IS_CARRYING = 3
    IS_WIELDING = 4
    IS_WEARING = 5
    HAS_BACKSTORY = 6
    HAS_PERSONA = 7
    HAS_DESCRIPTION = 8
    IS_DEAD = 9
    HAS_DAMAGE_LEVEL = 10
    HAS_HEALTH_LEVEL = 11
    HAS_STRENGTH_LEVEL = 12
    HAS_PLAYER_CONTEXT = 13
    HAS_ATTRIBUTE = 14
    IS_GETTABLE = 15
    IS_DRINK = 16
    IS_FOOD = 17
    IS_CONTAINER = 18
    IS_SURFACE = 19
    IS_WEARABLE = 20
    IS_WIELDABLE = 21
    HAD_SAID = 22
    HAD_ACTED = 23
    OBSERVED = 24
    CONTAINS = 25


# edges from GraphEdges that reference 2 objects (used in creating secondary objects)
# first_edges are edges where the secondary object comes first (e.g. secondary IS_INSIDE primary)
# SECONDARY_FIRST_EDGES = [GraphEdges.IS_INSIDE.name]
SECONDARY_FIRST_EDGES = []
# last_edges are edges where the secondary object comes last (e.g. primary IS_CARRYING secondary)
SECONDARY_LAST_EDGES = [
    GraphEdges.IS_CARRYING.name,
    GraphEdges.IS_WIELDING.name,
    GraphEdges.IS_WEARING.name,
    GraphEdges.CONTAINS.name,
]


class FeatureTokens(Enum):
    GAME_STATE = 1
    STATE_CHANGE_HIST = 2
    AGENTS_HIST = 3
    ACTION = 4


class ElementType(Enum):
    ROOM = 1
    OBJECT = 2
    CHARACTER = 3


class GraphDropoutOptions(Enum):
    NAME = "name_do"
    ATTRIBUTE = "attribute_do"
    ROOM_NAME = "room_name_do"
    ROOM_DESCRIPTION = "room_description_do"
    ROOM_BACKSTORY = "room_backstory_do"
    ROOM_OBJECTS = "room_objects_do"
    ROOM_CHARACTERS = "room_characters_do"
    CONTAINED_OBJECTS = "contained_objects_do"
    WORN_OBJECTS = "worn_objects_do"
    WIELDED_OBJECTS = "wielded_objects_do"
    CARRYING_OBJECTS = "carrying_objects_do"
    PHYS_DESCRIPTION = "phys_description_do"
    PERSONA = "persona_do"
    CHARACTER_INSIDE_ROOM = "character_inside_room_do"
    CHARACTER_TYPE = "character_type_do"
    OBJECT_INSIDE_ROOM = "object_inside_room_do"
    OBJECT_TYPE = "object_type_do"
    OBJECT_IS_GETTABLE = "object_is_gettable_do"
    OBJECT_IS_DRINK = "object_is_drink_do"
    OBJECT_IS_FOOD = "object_is_food_do"
    OBJECT_IS_CONTAINER = "object_is_container_do"
    OBJECT_IS_SURFACE = "object_is_surface_do"
    OBJECT_IS_WEAPON = "object_is_weapon_do"
    OBJECT_IS_WEARABLE = "object_is_wearable_do"


# Some additional params to go with characters and objects
IS_IN_ROOM = "is_in_room"
SEEN_IN_TRAIN_DATA = "seen_in_train"
ONE_LEVEL_SELF_PLAY_KEY = "one_level_selfplay"


ROOM_ATTRIBUTES = (
    "db_id",
    "base_id",
    "category",
    "setting",
    "description",
    "background",
    "neighbors",
    "possible_connections",
    "data_split",
)

ROOM_OBJECT_ATTRIBUTES = (
    "db_id",
    "base_id",
    "name",
    "description",
    "name_prefix",
    "is_plural",
    "is_gettable",
    "is_wearable",
    "is_weapon",
    "is_food",
    "is_drink",
    "is_container",
    "is_surface",
    "base_form",
    "data_split",
)

ROOM_CHARACTER_ATTRIBUTES = (
    "db_id",
    "base_id",
    "name",
    "name_prefix",
    "persona",
    "desc",
    "char_type",
    "is_plural",
)

OBJECT_INTERESTING_ATTRIBUTES = (
    "description",
    # 'is_plural',
    # 'is_gettable',
    # 'is_wearable',
    # 'is_weapon',
    # 'is_food',
    # 'is_drink',
    # 'is_container',
    # 'is_surface',
)

CHARACTER_INTERESTING_ATTRIBUTES = (
    "persona",
    "desc",
    # 'is_plural',
)

# The number of actions to sample for rollout during self-play
SELF_PLAY_ACTIONS_SAMPLE_SIZE = 1

# List of events to generate as potential (valid or invalid) actions.
POTENTIAL_EVENTS_TO_CHECK = (
    GoEvent,
    UnfollowEvent,
    FollowEvent,
    UnblockEvent,
    BlockEvent,
    HelpEvent,
    HitEvent,
    HugEvent,
    GetObjectEvent,
    PutObjectInEvent,
    DropObjectEvent,
    StealObjectEvent,
    GiveObjectEvent,
    EquipObjectEvent,
    WearEvent,
    WieldEvent,
    RemoveObjectEvent,
    IngestEvent,
    EatEvent,
    DrinkEvent,
)

ABSTRACT_AGENT_WARNING_MESSAGE = "WARNING: you are using an abstract agent"

is_simple = True

ATTRIBUTE_VALUES = {
    "IS_GETTABLE": {
        0: ("not gettable",)
        if is_simple
        else (
            "Is not gettable",
            "Can not be acquired",
        ),
        1: ("gettable",)
        if is_simple
        else (
            "Is gettable",
            "Can be picked up",
        ),
    },
    "IS_DRINK": {
        0: ("not drinkable",)
        if is_simple
        else (
            "Is not drinkable",
            "One can not drink this",
        ),
        1: ("drinkable",)
        if is_simple
        else (
            "Is drinkable",
            "One may drink this",
        ),
    },
    "IS_FOOD": {
        0: ("not edible",)
        if is_simple
        else (
            "Is not edible",
            "Can not be consumed as food",
            "not advisable to eat",
        ),
        1: ("edible",)
        if is_simple
        else (
            "Is ediable",
            "Is a source of nutritions",
        ),
    },
    "IS_CONTAINER": {
        0: ("not container",)
        if is_simple
        else (
            "Can not be used as a container",
            "Does not have any space for putting objects inside it",
        ),
        1: ("container",)
        if is_simple
        else (
            "Can be used as a container",
            "Has some space inside it that can keep other objects",
        ),
    },
    "IS_SURFACE": {
        0: ("not surface",)
        if is_simple
        else (
            "Can not have things on top of it",
            "Does not have any surface for putting objects on it",
        ),
        1: ("surface",)
        if is_simple
        else (
            "Can have things on top of it",
            "Has a surface for putting objects on it",
        ),
    },
    "IS_WIELDABLE": {
        0: ("not wieldable",)
        if is_simple
        else (
            "Can not be used as a weapon",
            "Can not be wielded",
            "Is not a weapon",
        ),
        1: ("wieldable",)
        if is_simple
        else (
            "Can be a weapon",
            "Can be wielded",
            "Is a weapon",
        ),
    },
    "IS_WEARABLE": {
        0: ("not wearable",)
        if is_simple
        else (
            "Can not be worn",
            "Is not wearable",
        ),
        1: ("wearable",)
        if is_simple
        else (
            "Can be worn",
            "Is wearable",
        ),
    },
}

new_prompts = True
# new_prompts = False

TEACHER_PROMPTS = {
    "room_description": ["describe", "describe the room"],
    "room_backstory": ["background", "describe the room backstory", "room backstory"],
    "adding_physical_description": ["describe {name}", "examine {name}"],
    "adding_objects": ["add object", "add a new object", "suggest a new object"],
    "adding_object_contains": [
        "what objects are inside of {name}",
        "what is contained by {name}",
        "what does {name} contain" if new_prompts else "what objects does {name} have",
        # 'what objects does {name} have',
    ],
    "adding_characters": [
        "add character",
        "add a new character",
        "suggest a new character",
    ],
    "adding_character_wielding": [
        "what is wielded by {name}",
        "what weapons are used by {name}",
        "what is {name} wielding",
    ],
    "adding_character_carrying": [
        "what is carried by {name}",
        "what belongs to {name}",
        "what is {name} carrying",
    ],
    "adding_character_wearing": ["what is worn by {name}", "what does {name} wear"],
    "adding_character_persona": [
        "what is the persona of {name}",
        "describe the persona of {name}"
        if new_prompts
        else "what persona does {name} have"
        # 'what persona does {name} have',
    ],
    "add_item_type": [
        "what is the type of {name}",
        "what type is {name}",
        "what type of item is {name}",
        "{name} is what type",
    ],
    "action_effects": [
        "how world changes if {actor} {act}",
        "what will changes if {actor} {act}",
        "describe changes after {actor} {act}",
    ],
    "narration_after_action": [
        "what {actor} sees after {act}",
        "tell {actor} what happens after {act}",
    ],
    "attribute_qa_gettable": [
        "Is {name} gettable?",
        "Can I pick up {name}?",
    ],
    "attribute_qa_drink": [
        "Is {name} drinkable?",
        "Can I drink {name}?",
    ],
    "attribute_qa_food": [
        "Is {name} edible?",
        "Can I eat {name}?",
        "Is {name} a food?",
    ],
    "attribute_qa_container": [
        "Is {name} container?",
        "Can I put something inside {name}?",
    ],
    "attribute_qa_surface": [
        "Does {name} have usable surface?",
        "Can I put something on {name}?",
    ],
    "attribute_qa_weapon": [
        "Is {name} a weapon?",
        "Can I use {name} as a weapon?",
    ],
    "attribute_qa_wearable": [
        "Is {name} wearable?",
        "Can I wear {name}?",
    ],
}
