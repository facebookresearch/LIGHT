#!/usr/bin/env python3
"""
LIGHT common sense task agents.
"""

from abc import abstractmethod
from collections import defaultdict
import copy
import json
import jsonlines
from typing import List, Optional, Tuple
import random
import os

# from parlai.tasks.jericho_world.agents import encode_set_elements
from typing import Any, Dict, List, Set, Union, Optional, Tuple


def encode_set_elements(set1: Set[str], set2: Set[str]) -> Tuple[List[str]]:
    """
    Encodes (maps to int indices) elements in the union of two sets.
    """
    set1_enc = []
    set2_enc = []
    for el_id, el in enumerate(set1.union(set2)):
        el_id_str = str(el_id)
        if el in set1:
            set1_enc.append(el_id_str)
        if el in set2:
            set2_enc.append(el_id_str)
    return set1_enc, set2_enc


from parlai.core.message import Message
from parlai.core.metrics import F1Metric
from parlai.core.params import ParlaiParser
from parlai.utils import logging
from parlai.core.teachers import DialogTeacher
from parlai.core.loader import register_teacher

from light.modeling.tasks.common_sense.build import (
    get_dtype,
)
import light.modeling.tasks.common_sense.constants as consts
from light.modeling.tasks.common_sense.build import build


def clean_str(txt):
    # ensure txt is str, could be int/float
    txt = str(txt)
    for char in ("\n", "\t"):
        txt = txt.replace(char, " ")
    return txt


def graph_state_tuple(v1, v2, edge):
    edge_name = edge if isinstance(edge, str) else edge.name
    return consts.GRAPH_TUPLES_DELIM.join([clean_str(v1), edge_name, clean_str(v2)])


def add_to_graph_state(graphs_state, v1, v2, edge):
    graphs_state.append(graph_state_tuple(v1, v2, edge))


def get_mutation_token(mutation_type):
    assert isinstance(mutation_type, consts.GraphMutations), "Invalid mutation type"
    return f"{mutation_type.name}:"


def get_mutation(tuple, mutation_type):
    return f"{get_mutation_token(mutation_type)} {tuple}"


def survives_dropout(prob_do: float):
    assert (
        0 <= prob_do <= 1
    ), f"Invalid probably of dropout: {prob_do}. Must be in [0, 1]."
    if 0 < prob_do < 1:
        return random.random() > prob_do
    return prob_do == 0


def replace_binarized_attributes_with_description(states_str: str):
    if states_str == consts.GraphMutations.NO_MUTATION.name:
        return states_str

    states = states_str.split(consts.GRAPH_STATES_DELIM)
    for st_id in range(len(states)):
        curr_state = states[st_id]

        if "HAD_ACTED" in curr_state:
            # Game action history
            continue

        v1, e, v2 = curr_state.split(consts.GRAPH_TUPLES_DELIM)
        if e not in consts.ATTRIBUTE_VALUES:
            continue

        # Replacing binarized state with their equivalent text
        assert v2 in (
            "0",
            "1",
        ), f"unsupported binary value {v2} for {e}"
        attribute_text_equivalent = random.choice(consts.ATTRIBUTE_VALUES[e][int(v2)])
        states[st_id] = graph_state_tuple(
            v1, attribute_text_equivalent, consts.GraphEdges.HAS_ATTRIBUTE
        )

    return consts.GRAPH_STATES_DELIM.join(states)


def float_to_binary_str(float_value):
    """
    Changing a float value in [0, 1] binary 0 or 1 string.
    """
    return str(int(float_value > consts.ATTRIBUTE_VALUE_THRESHOLD))


def dedup_elements_list(elements_list, pick_first=False):
    """
    Deduplicates the elements with the same name from the `elements_list`.

    Duplicate elements might be duplicate only in name (having different attributes,
    personas etc.). Therefore, there is an option to sample between them at random
    (intended for training) or pick and arbitrary (first) one. Random sampling happens
    when `pick_first` is False.
    """
    entities_by_name = defaultdict(list)
    for element in elements_list:
        element_name = element["name"]
        entities_by_name[element_name].append(element)

    deduped_elements = []
    for elements_with_name in entities_by_name.values():
        if pick_first or len(elements_with_name) == 1:
            deduped_elements.append(elements_with_name[0])
        else:
            deduped_elements.append(random.choice(elements_with_name))

    return deduped_elements


def remove_train_items(elements_list, dtype="train"):
    new_elements_list = []
    for element in elements_list:
        if (
            dtype is not None
            and element[consts.SEEN_IN_TRAIN_DATA]
            and dtype != "train"
        ):
            continue
        new_elements_list.append(element)
    return new_elements_list


def add_room_att_to_graph_states(
    room_data,
    states,
    dropouts,
    dropout_default=0,
):
    # Adding room level info to the graph state
    room_name = room_data["setting"]
    if survives_dropout(
        dropouts.get(consts.GraphDropoutOptions.ROOM_NAME, dropout_default)
    ):
        add_to_graph_state(
            states, room_name, consts.ElementType.ROOM.name, consts.GraphEdges.IS_TYPE
        )

    # Maybe adding room description
    if survives_dropout(
        dropouts.get(consts.GraphDropoutOptions.ROOM_DESCRIPTION, dropout_default)
    ):
        room_description = room_data["description"]
        add_to_graph_state(
            states, room_name, room_description, consts.GraphEdges.HAS_DESCRIPTION
        )

    # Maybe adding backstory
    if survives_dropout(
        dropouts.get(consts.GraphDropoutOptions.ROOM_BACKSTORY, dropout_default)
    ):
        room_baskstory = room_data["background"]
        add_to_graph_state(
            states, room_name, room_baskstory, consts.GraphEdges.HAS_BACKSTORY
        )


def add_subelements(
    states, parent, children, edge, do_prob, type_do=0, reverse_edge=False
):
    """
    Add the vertices from `children` list to the `parent` in the `states` graph.
    """
    for child_vert_name in children:
        if not survives_dropout(do_prob):
            continue

        if survives_dropout(type_do):
            add_to_graph_state(
                states,
                child_vert_name,
                # So far all the sub-component ndoes seem to be objects, but this may change in the future
                consts.ElementType.OBJECT.name,
                consts.GraphEdges.IS_TYPE,
            )
        if reverse_edge:
            add_to_graph_state(states, parent, child_vert_name, edge)
        else:
            add_to_graph_state(states, child_vert_name, parent, edge)


def add_room_objects_to_graph_state(
    room_data, states, only_in_edges, dropouts, dropout_default=0
):
    for obj in dedup_elements_list(room_data["objects"]):
        if only_in_edges and not obj[consts.IS_IN_ROOM]:
            # it is an object on the ex edge
            continue
        if not survives_dropout(
            dropouts.get(consts.GraphDropoutOptions.ROOM_OBJECTS, dropout_default)
        ):
            continue

        room_name = room_data["setting"]
        object_name = obj["name"]

        if survives_dropout(
            dropouts.get(consts.GraphDropoutOptions.OBJECT_INSIDE_ROOM, dropout_default)
        ):
            # Adding the object itself
            add_to_graph_state(
                states, object_name, room_name, consts.GraphEdges.IS_INSIDE
            )

        for edge_type_do, edge_type, edge_value in (
            (
                consts.GraphDropoutOptions.OBJECT_TYPE,
                consts.GraphEdges.IS_TYPE,
                consts.ElementType.OBJECT.name,
            ),
            (
                consts.GraphDropoutOptions.OBJECT_IS_GETTABLE,
                consts.GraphEdges.IS_GETTABLE,
                obj.get("is_gettable", None),
            ),
            (
                consts.GraphDropoutOptions.OBJECT_IS_DRINK,
                consts.GraphEdges.IS_DRINK,
                obj.get("is_drink", None),
            ),
            (
                consts.GraphDropoutOptions.OBJECT_IS_FOOD,
                consts.GraphEdges.IS_FOOD,
                obj.get("is_food", None),
            ),
            (
                consts.GraphDropoutOptions.OBJECT_IS_CONTAINER,
                consts.GraphEdges.IS_CONTAINER,
                obj.get("is_container", None),
            ),
            (
                consts.GraphDropoutOptions.OBJECT_IS_SURFACE,
                consts.GraphEdges.IS_SURFACE,
                obj.get("is_surface", None),
            ),
            (
                consts.GraphDropoutOptions.OBJECT_IS_WEAPON,
                consts.GraphEdges.IS_WIELDABLE,
                obj.get("is_weapon", None),
            ),
            (
                consts.GraphDropoutOptions.OBJECT_IS_WEARABLE,
                consts.GraphEdges.IS_WEARABLE,
                obj.get("is_wearable", None),
            ),
        ):
            # if attribute doesn't exist, edge value is None
            if edge_value is not None:
                if survives_dropout(dropouts.get(edge_type_do, dropout_default)):
                    if isinstance(edge_value, float):
                        # Changing it to be an int value 0-10
                        edge_value = float_to_binary_str(edge_value)
                    # Adding the object type
                    add_to_graph_state(
                        states,
                        object_name,
                        edge_value,
                        edge_type,
                    )

        if "description" in obj and survives_dropout(
            dropouts.get(consts.GraphDropoutOptions.PHYS_DESCRIPTION, dropout_default)
        ):
            edge = consts.GraphEdges.HAS_DESCRIPTION
            add_to_graph_state(states, object_name, obj["description"], edge)

        # Adding contained objects
        if "containing_objects" in obj:
            add_subelements(
                states,
                object_name,
                obj["containing_objects"],
                consts.GraphEdges.CONTAINS,
                # consts.GraphEdges.IS_INSIDE,
                dropouts.get(
                    consts.GraphDropoutOptions.CONTAINED_OBJECTS, dropout_default
                ),
                reverse_edge=True,
                # reverse_edge=False,
                type_do=dropouts.get(
                    consts.GraphDropoutOptions.OBJECT_TYPE, dropout_default
                ),
            )


def add_room_characters_to_graph_state(
    room_data,
    states,
    only_in_edges,
    dropouts,
    dropout_default=0,
):
    def get_names(objects_list):
        # creating the list from a set, to avoid duplicate elements.
        return list({o["name"] for o in objects_list})

    room_name = room_data["setting"]
    for char in dedup_elements_list(room_data["characters"]):
        if only_in_edges and not char[consts.IS_IN_ROOM]:
            continue
        if not survives_dropout(
            dropouts.get(consts.GraphDropoutOptions.ROOM_CHARACTERS, dropout_default)
        ):
            continue

        character_name = char["name"]

        if survives_dropout(
            dropouts.get(consts.GraphDropoutOptions.CHARACTER_TYPE, dropout_default)
        ):
            # Adding the character itself
            add_to_graph_state(
                states,
                character_name,
                consts.ElementType.CHARACTER.name,
                consts.GraphEdges.IS_TYPE,
            )

        if survives_dropout(
            dropouts.get(
                consts.GraphDropoutOptions.CHARACTER_INSIDE_ROOM, dropout_default
            )
        ):
            add_to_graph_state(
                states, character_name, room_name, consts.GraphEdges.IS_INSIDE
            )

        if "desc" in char and survives_dropout(
            dropouts.get(consts.GraphDropoutOptions.PHYS_DESCRIPTION, dropout_default)
        ):
            edge = consts.GraphEdges.HAS_DESCRIPTION
            add_to_graph_state(states, character_name, char["desc"], edge)

        if "persona" in char and survives_dropout(
            dropouts.get(consts.GraphDropoutOptions.PERSONA, dropout_default)
        ):
            edge = consts.GraphEdges.HAS_PERSONA
            add_to_graph_state(states, character_name, char["persona"], edge)

        # Adding carrying, wielding and wearing objects
        if "wielding_objects" in char:
            add_subelements(
                states,
                character_name,
                get_names(char["wielding_objects"]),
                consts.GraphEdges.IS_WIELDING,
                dropouts.get(
                    consts.GraphDropoutOptions.WIELDED_OBJECTS, dropout_default
                ),
                reverse_edge=True,
                type_do=dropouts.get(
                    consts.GraphDropoutOptions.CHARACTER_TYPE, dropout_default
                ),
            )
        if "wearing_objects" in char:
            add_subelements(
                states,
                character_name,
                get_names(char["wearing_objects"]),
                consts.GraphEdges.IS_WEARING,
                dropouts.get(consts.GraphDropoutOptions.WORN_OBJECTS, dropout_default),
                reverse_edge=True,
                type_do=dropouts.get(
                    consts.GraphDropoutOptions.CHARACTER_TYPE, dropout_default
                ),
            )
        if "carrying_objects" in char:
            add_subelements(
                states,
                character_name,
                get_names(char["carrying_objects"]),
                consts.GraphEdges.IS_CARRYING,
                dropouts.get(
                    consts.GraphDropoutOptions.CARRYING_OBJECTS, dropout_default
                ),
                reverse_edge=True,
                type_do=dropouts.get(
                    consts.GraphDropoutOptions.CHARACTER_TYPE, dropout_default
                ),
            )


def generate_graph_tuples(
    room_state,
    element_types: List[consts.ElementType],
    dropouts,
    only_in_edges=True,
    dropouts_default=0,
    label_tuples=None,
    remove_reference=False,
):
    """
    Convert the room state into a list of graph tuples of format x -=- edge -=- y
    Note: label_tuples should be an iterable (ideally a set) of graph tuples that
    are present in the label and therefore should not be included in this list.
    remove_reference adds to this restriction and is only used when label_tuples exists
    """

    state_tuples_list = []

    if consts.ElementType.ROOM in element_types:
        add_room_att_to_graph_states(
            room_state, state_tuples_list, dropouts, dropouts_default
        )

    if consts.ElementType.OBJECT in element_types:
        add_room_objects_to_graph_state(
            room_state, state_tuples_list, only_in_edges, dropouts, dropouts_default
        )

    if consts.ElementType.CHARACTER in element_types:
        add_room_characters_to_graph_state(
            room_state, state_tuples_list, only_in_edges, dropouts, dropouts_default
        )
    # In order to make the default label tuple argument immutable, do extra type checking here
    if type(label_tuples) is list or type(label_tuples) is set:
        #
        state_tuples_list = [t for t in state_tuples_list if t not in label_tuples]

        if remove_reference:
            # A non-ideal way of doing this, but in addition to explicitly used label_tuples we also don't want to
            # include tuples who contain the label result. For example, x -=- contains -=- y, we don't want y to already exist
            # as an object in the room so we remove labels like y -=- is_type -=- object
            referenced_objects = []
            for t in label_tuples:
                split = t.split(consts.GRAPH_TUPLES_DELIM)
                # in no_mutation case, label_tuples will be [''] so split will have length 1
                if len(split) == 3:
                    referenced_objects.append(split[2])

            referenced_objects = set(referenced_objects)

            new_state_tuples_list = []
            for t in state_tuples_list:
                # split tuple into y edge z, we want y to not be the new item
                split = t.split(consts.GRAPH_TUPLES_DELIM)
                if split[0] not in referenced_objects:
                    new_state_tuples_list.append(t)

            state_tuples_list = new_state_tuples_list

    return consts.GRAPH_STATES_DELIM.join(state_tuples_list)


class CommonSenseBaseTeacher(DialogTeacher):
    """
    Base class for all the common sense teachers.
    """

    def __init__(self, opt, shared=None):
        build(opt)
        self._delimiter = opt["delimiter"]
        self._dtype = get_dtype(opt)
        self.id = self.get_id()
        self._text_features_droputs = {
            consts.GraphDropoutOptions.ROOM_NAME: opt["room_name_do"],
            consts.GraphDropoutOptions.ROOM_DESCRIPTION: opt["room_description_do"],
            consts.GraphDropoutOptions.ROOM_BACKSTORY: opt["room_backstory_do"],
            consts.GraphDropoutOptions.ROOM_OBJECTS: opt["room_objects_do"],
            consts.GraphDropoutOptions.ROOM_CHARACTERS: opt["room_characters_do"],
            consts.GraphDropoutOptions.CONTAINED_OBJECTS: opt["contained_objects_do"],
            consts.GraphDropoutOptions.WORN_OBJECTS: opt["worn_objects_do"],
            consts.GraphDropoutOptions.WIELDED_OBJECTS: opt["wielded_objects_do"],
            consts.GraphDropoutOptions.CARRYING_OBJECTS: opt["carrying_objects_do"],
            consts.GraphDropoutOptions.ATTRIBUTE: opt["attribute_do"],
            consts.GraphDropoutOptions.PERSONA: opt["persona_do"],
            consts.GraphDropoutOptions.PHYS_DESCRIPTION: opt["phys_description_do"],
            consts.GraphDropoutOptions.CHARACTER_INSIDE_ROOM: opt[
                "character_inside_room_do"
            ],
            consts.GraphDropoutOptions.CHARACTER_TYPE: opt["character_type_do"],
            consts.GraphDropoutOptions.OBJECT_INSIDE_ROOM: opt["object_inside_room_do"],
            consts.GraphDropoutOptions.OBJECT_TYPE: opt["object_type_do"],
            consts.GraphDropoutOptions.OBJECT_IS_GETTABLE: opt[
                "attribute_qa_gettable_do"
            ],
            consts.GraphDropoutOptions.OBJECT_IS_DRINK: opt["attribute_qa_drink_do"],
            consts.GraphDropoutOptions.OBJECT_IS_FOOD: opt["attribute_qa_food_do"],
            consts.GraphDropoutOptions.OBJECT_IS_CONTAINER: opt[
                "attribute_qa_container_do"
            ],
            consts.GraphDropoutOptions.OBJECT_IS_SURFACE: opt[
                "attribute_qa_surface_do"
            ],
            consts.GraphDropoutOptions.OBJECT_IS_WEAPON: opt["attribute_qa_weapon_do"],
            consts.GraphDropoutOptions.OBJECT_IS_WEARABLE: opt[
                "attribute_qa_wearable_do"
            ],
        }
        self.no_mutation_weight = opt["no_mutation_weight"]
        super().__init__(opt, shared)

    @classmethod
    def add_cmdline_args(cls, parser: ParlaiParser, partial_opt=None) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        arg_group = parser.add_argument_group("LIGHT common sense teachers.")
        arg_group.add_argument(
            "--delimiter",
            type=str,
            default="\n",
            help=("Delimiter token between the parts of the example text feature."),
        )
        arg_group.add_argument(
            "--room-name-do",
            type=float,
            default=0,
            help="The dropout rate for the room name.",
        )
        arg_group.add_argument(
            "--room-description-do",
            type=float,
            default=0,
            help="The dropout rate for the room description.",
        )
        arg_group.add_argument(
            "--room-backstory-do",
            type=float,
            default=0,
            help="The dropout rate for the room backstory.",
        )
        arg_group.add_argument(
            "--room-elements-type",
            type=str,
            choices=["objects", "characters", "both"],
            default="both",
            help="The type of room content elements to keep.",
        )
        arg_group.add_argument(
            "--room-objects-do",
            type=float,
            default=0,
            help="The dropout rate for objects in the room.",
        )
        arg_group.add_argument(
            "--room-characters-do",
            type=float,
            default=0,
            help="The dropout rate for characters in the room.",
        )
        arg_group.add_argument(
            "--contained-objects-do",
            type=float,
            default=0,
            help="The dropout rate for objects contained within other objects.",
        )
        arg_group.add_argument(
            "--worn-objects-do",
            type=float,
            default=0,
            help="The dropout rate for objects worn by characters.",
        )
        arg_group.add_argument(
            "--wielded-objects-do",
            type=float,
            default=0,
            help="The dropout rate for objects wielded by characters.",
        )
        arg_group.add_argument(
            "--carrying-objects-do",
            type=float,
            default=0,
            help="The dropout rate for objects carried by characters.",
        )
        arg_group.add_argument(
            "--attribute-do",
            type=float,
            default=0,
            help="The dropout rate for character/object attributes",
        )
        arg_group.add_argument(
            "--phys-description-do",
            type=float,
            default=0,
            help="The dropout rate for character/object physical descriptions",
        )
        arg_group.add_argument(
            "--persona-do",
            type=float,
            default=0,
            help="The dropout rate for character personas",
        )
        arg_group.add_argument(
            "--character-inside-room-do",
            type=float,
            default=0,
            help="The dropout rate for the KB line character in room",
        )
        arg_group.add_argument(
            "--character-type-do",
            type=float,
            default=0,
            help="The dropout rate for chracter type KB line",
        )
        arg_group.add_argument(
            "--object-inside-room-do",
            type=float,
            default=0,
            help="The dropout rate for KB line object in room",
        )
        arg_group.add_argument(
            "--object-type-do",
            type=float,
            default=0,
            help="The dropout rate for object type KB line",
        )
        arg_group.add_argument(
            "--no-mutation-weight",
            type=float,
            default=1,
            help="The default weighting of no mutation options (when picking from a list), smaller values make less likely",
        )
        # Object attribute dropouts
        arg_group.add_argument(
            "--attribute-qa-gettable-do",
            type=float,
            default=0,
            help=("The dropout for the gettable attribute."),
        )
        arg_group.add_argument(
            "--attribute-qa-drink-do",
            type=float,
            default=0,
            help=("The dropout for the drinkable attribute."),
        )
        arg_group.add_argument(
            "--attribute-qa-food-do",
            type=float,
            default=0,
            help=("The dropout for the edible attribute."),
        )
        arg_group.add_argument(
            "--attribute-qa-container-do",
            type=float,
            default=0,
            help=("The dropout for the container attribute."),
        )
        arg_group.add_argument(
            "--attribute-qa-surface-do",
            type=float,
            default=0,
            help=("The dropout for the is_surface attribute."),
        )
        arg_group.add_argument(
            "--attribute-qa-weapon-do",
            type=float,
            default=0,
            help=("The dropout for the wieldable attribute."),
        )
        arg_group.add_argument(
            "--attribute-qa-wearable-do",
            type=float,
            default=0,
            help=("The dropout for the wearable attribute."),
        )
        return parser

    @abstractmethod
    def get_id(self):
        """
        Returns teacher's id.
        """

    @abstractmethod
    def generate_example_text(self, data_dict):
        """
        Generates example *text* from a dict of data.
        """

    @abstractmethod
    def generate_example_label(self, data_dict):
        """
        Generates example *label* from a dict of data.
        """

    @abstractmethod
    def get_teacher_prompt(self, data_dict=None, name=""):
        """
        Retruns the teacher prompt from a dict of available data.
        """

    def custom_evaluation(
        self,
        teacher_action: Message,
        labels: Optional[Tuple[str]],
        model_response: Message,
    ) -> None:
        if model_response.is_padding() or (not model_response.get("text", None)):
            return

        expected_graph = set(labels[0].lower().split(consts.GRAPH_STATES_DELIM))
        predicted_graph = set(
            model_response["text"].lower().split(consts.GRAPH_STATES_DELIM)
        )

        # Encoding the graph edges/mutation operations into ints for readily use of F1Metric
        # Mutation: Subject, Relation , Object
        expected_graph_enc, predicted_graph_enc = encode_set_elements(
            expected_graph, predicted_graph
        )
        self.metrics.add(
            "response_elements_f1",
            F1Metric.compute(
                guess=" ".join(predicted_graph_enc),
                answers=[" ".join(expected_graph_enc)],
            ),
        )

        # Mutation: Subject, Relation F1
        ekg_sub_rel = set(
            [e.rsplit(consts.GRAPH_TUPLES_DELIM, 1)[0] for e in expected_graph]
        )
        pkg_sub_rel = set(
            [e.rsplit(consts.GRAPH_TUPLES_DELIM, 1)[0] for e in predicted_graph]
        )
        ekg_sub_rel_ids, pkg_sub_rel_ids = encode_set_elements(ekg_sub_rel, pkg_sub_rel)
        self.metrics.add(
            "graph_subject_relation_f1",
            F1Metric.compute(
                guess=" ".join(pkg_sub_rel_ids), answers=[" ".join(ekg_sub_rel_ids)]
            ),
        )

        # Mutation: Subject F1
        ekg_sub = set([e.split(consts.GRAPH_TUPLES_DELIM)[0] for e in ekg_sub_rel])
        pkg_sub = set([e.split(consts.GRAPH_TUPLES_DELIM)[0] for e in pkg_sub_rel])
        ekg_sub_ids, pkg_sub_ids = encode_set_elements(ekg_sub, pkg_sub)
        self.metrics.add(
            "graph_subject_f1",
            F1Metric.compute(
                guess=" ".join(pkg_sub_ids), answers=[" ".join(ekg_sub_ids)]
            ),
        )


##################################################################################################
#
#               Room and world common sense teachers
#
##################################################################################################


class RoomCommonSenseBaseTeacher(CommonSenseBaseTeacher):
    """
    Common sense for rooms and their content (Abstract class).
    """

    def __init__(self, opt, shared=None):
        opt = copy.deepcopy(opt)
        self._include_ex_room_entities = opt["include_ex_room_entities"]
        self._room_elements_type = opt["room_elements_type"]
        opt["datafile"] = self._get_datafile_path(opt)
        super().__init__(opt, shared)

    def collect_dropouts(self, opt):
        self._dropouts = dict()
        for k in self.DROPOUT_KEYS:
            self._dropouts[k] = opt[k]

    @classmethod
    def add_cmdline_args(cls, parser: ParlaiParser, partial_opt=None) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        arg_group = parser.add_argument_group(
            "LIGHT room entities common sense teacher arguments."
        )
        arg_group.add_argument(
            "--include-ex-room-entities",
            type="bool",
            default=False,
            help=(
                "Whether to include the room entities that are on the ex edge (might be in the room)."
            ),
        )
        return parser

    def _get_datafile_path(self, opt):
        return os.path.join(
            opt["datapath"],
            consts.DATASET_DIR_NAME,
            consts.ROOM_CONTENTS_DIR,
            f"{get_dtype(opt)}.jsonl",
        )

    def load_room_content_data(self, datapath: str):
        logging.info(f"Loading data from {datapath}")
        with jsonlines.open(datapath, "r") as fi:
            return [rd for rd in fi]

    def setup_data(self, datapath: str):
        room_content_data = self.load_room_content_data(datapath)
        for rc in room_content_data:
            message = Message(
                {
                    "id": self.id,
                    # To have randomization and dropouts, we set text later.
                    # The final message and label for each example is determined
                    # the content of the `original_room_content_data`
                    "text": "text place holder",
                    "labels": ["label place holder"],
                    "original_room_content_data": rc,
                }
            )
            yield message, True

    def clean_example(self, room_content_data):
        """
        Returns a cleaned copy of the example that is safe to change.

        It de-duplicates the items in the room, based on their names. De-duplication
        happens with random selection among the items during training, and choosing the
        first element only during valid and test (for repeatability).
        """
        example_copy = copy.deepcopy(room_content_data)
        room_data = example_copy["original_room_content_data"]
        # We only pick the first element from the list during valid and test,
        # but select as random during the training.
        non_randomize_dedup = self._dtype in ("valid", "test")
        for item_type in ("objects", "characters"):
            room_data[item_type] = dedup_elements_list(
                room_data[item_type], pick_first=non_randomize_dedup
            )
        return example_copy

    def get(self, episode_idx, entry_idx=0):
        return self.clean_example(super().get(episode_idx, entry_idx=entry_idx))


class RoomDescriptionAndBackStorydBase(RoomCommonSenseBaseTeacher):
    """
    The abstract base class for generating room descriptions and backstoru.
    """

    def get(self, episode_idx, entry_idx=0):
        new_message = super().get(episode_idx, entry_idx=entry_idx)
        room_content_data = new_message.pop("original_room_content_data")

        new_message.force_set(
            "text",
            self._delimiter.join(
                [
                    replace_binarized_attributes_with_description(
                        self.generate_example_text(room_content_data)
                    ),
                    self.get_teacher_prompt(),
                ]
            ),
        )
        new_message.force_set(
            "labels",
            [
                replace_binarized_attributes_with_description(
                    self.generate_example_label(room_content_data)
                )
            ],
        )
        return new_message


@register_teacher("light:common_sense:RoomDescriptionTeacher")
class RoomDescriptionTeacher(RoomDescriptionAndBackStorydBase):
    """
    Generates room description from its state graph.
    """

    def get_id(self):
        return "RoomDescriptionTeacher"

    def generate_example_text(self, room_content_data):
        element_types = [
            consts.ElementType.ROOM,
            consts.ElementType.OBJECT,
            consts.ElementType.CHARACTER,
        ]
        self._text_features_droputs[consts.GraphDropoutOptions.ROOM_DESCRIPTION] = 1
        return generate_graph_tuples(
            room_content_data,
            element_types,
            only_in_edges=not self._include_ex_room_entities,
            dropouts=self._text_features_droputs,
        )

    def generate_example_label(self, room_content_data):
        element_types = [consts.ElementType.ROOM]
        missing_graph_states_str = generate_graph_tuples(
            room_content_data,
            element_types,
            dropouts={
                consts.GraphDropoutOptions.ROOM_NAME: 1,
                consts.GraphDropoutOptions.ROOM_BACKSTORY: 1,
            },
        )
        missing_graph_states = missing_graph_states_str.split(consts.GRAPH_STATES_DELIM)
        mutations = [
            get_mutation(gs, consts.GraphMutations.ADD) for gs in missing_graph_states
        ]
        return consts.GRAPH_STATES_DELIM.join(mutations)

    def get_teacher_prompt(self):
        return random.choice(consts.TEACHER_PROMPTS["room_description"])


@register_teacher("light:common_sense:RoomBackstoryTeacher")
class RoomBackstoryTeacher(RoomDescriptionAndBackStorydBase):
    """
    Generates room backstory from its state graph.
    """

    def get_id(self):
        return "RoomBackstoryTeacher"

    def generate_example_text(self, room_content_data):
        element_types = [
            consts.ElementType.ROOM,
            consts.ElementType.OBJECT,
            consts.ElementType.CHARACTER,
        ]
        self._text_features_droputs[consts.GraphDropoutOptions.ROOM_BACKSTORY] = 1
        return generate_graph_tuples(
            room_content_data,
            element_types,
            only_in_edges=not self._include_ex_room_entities,
            dropouts=self._text_features_droputs,
        )

    def generate_example_label(self, room_content_data):
        element_types = [consts.ElementType.ROOM]
        missing_graph_states_str = generate_graph_tuples(
            room_content_data,
            element_types,
            dropouts={
                consts.GraphDropoutOptions.ROOM_NAME: 1,
                consts.GraphDropoutOptions.ROOM_DESCRIPTION: 1,
            },
        )
        missing_graph_states = missing_graph_states_str.split(consts.GRAPH_STATES_DELIM)
        mutations = [
            get_mutation(gs, consts.GraphMutations.ADD) for gs in missing_graph_states
        ]
        return consts.GRAPH_STATES_DELIM.join(mutations)

    def get_teacher_prompt(self):
        return random.choice(consts.TEACHER_PROMPTS["room_backstory"])


class RoomElementBase(RoomCommonSenseBaseTeacher):
    """
    Base teacher for adding room characters and objects.
    """

    def setup_data(self, datapath: str):
        def had_nothing_to_add(example):
            element_types = self._room_element_types()
            req_elements = []
            for element_type in element_types:
                elements = example["original_room_content_data"][element_type]
                req_elements.extend(elements)

            if not self._include_ex_room_entities:
                req_elements = [re for re in req_elements if re[consts.IS_IN_ROOM]]
            return len(req_elements) == 0

        for example, _ in super().setup_data(datapath):
            example["end_adding_example"] = False
            for item_type in ("objects", "characters"):
                room_items = example["original_room_content_data"][item_type]
                example["original_room_content_data"][item_type] = remove_train_items(
                    room_items, dtype=self._dtype
                )
            if had_nothing_to_add(example):
                continue
            yield example, True

    @abstractmethod
    def _room_element_types(self):
        """
        The type of element to suggest adding to the room state.
        """

    @abstractmethod
    def generate_element_graph_states(self, room_name, element):
        """
        Generates the details of the added element itself and its subcomponents.
        """

    def delete_label_item(self):
        """
        Whether to delete the label item from the room content, used to indicate this
        item didn't exist before this mutation.
        """
        return True

    def add_no_mutation_option(self):
        """
        Whether to add a buffer for no mutation, true if it makes sense for entire
        object to be included in context.
        """
        return True

    def remove_endpoint_references(self):
        """
        Whether to remove the referenced item's other states in the context For example,
        if the labels is x -=- contains -=- y then y -=- is_type -=- object shouldn't be
        in the context.
        """
        return False

    def select_from_available_mutations(self):
        return False

    def pick_label(self, potential_labels, room_name):
        """
        Returns label_mutation, label_name, label_graph_tuple.

        label_mutation is the actual label to be returned, includes ADD: marker
        label_name is the name of the item this label is about (e.g. obj being
        described) label_graph_tuple is the underlying state that the mutation is
        derived from, used to remove from context
        """
        # This return structure is somewhat clunky but allows us to handle a variety of cases and reduce
        # manual string parsing

        # No element to add, should never happen due to setup data ignoring no_add examples
        if not potential_labels:
            return consts.GraphMutations.NO_MUTATION.name, "", ""

        # Picking and element and its sub-components at random.
        # Extra overhead for sampling even when it is length 1, but it is alright.
        label_index = random.choice(range(len(potential_labels)))

        if self.select_from_available_mutations():
            no_mutation_indices = set()
            for i, label_item in enumerate(potential_labels):
                graph_states = self.generate_element_graph_states(room_name, label_item)
                if len(graph_states) == 0:
                    no_mutation_indices.add(i)
            try:
                label_index = random.choice(
                    [
                        i
                        for i in range(len(potential_labels))
                        if i not in no_mutation_indices
                    ]
                )
            except:
                pass

        if self.delete_label_item():
            label_item = potential_labels.pop(label_index)
        else:
            label_item = potential_labels[label_index]

        label_name = label_item["name"]

        new_graph_states = self.generate_element_graph_states(room_name, label_item)

        # if no new graph states, return no mutation
        if len(new_graph_states) == 0:
            return consts.GraphMutations.NO_MUTATION.name, label_name, ""

        # only predict one add-graph-state line at a time, include no-mutation option
        # buffer is 0 if we do not add a buffer and 1 if we do, we then check against the length
        no_mutation_weight = (
            0 if not self.add_no_mutation_option() else self.no_mutation_weight
        )
        num_states = len(new_graph_states)
        weights = [*[1 for i in range(num_states)], no_mutation_weight]
        label_graph_state_index = random.choices(
            range(num_states + 1), weights=weights
        )[0]
        if label_graph_state_index >= len(new_graph_states):
            return consts.GraphMutations.NO_MUTATION.name, label_name, ""

        # remove this graph state from label, return it
        label_graph_tuple = new_graph_states.pop(label_graph_state_index)

        return (
            get_mutation(label_graph_tuple, consts.GraphMutations.ADD),
            label_name,
            label_graph_tuple,
        )

    def get(self, episode_idx, entry_idx=0):
        new_message = super().get(episode_idx, entry_idx=entry_idx)
        room_content_data = new_message.pop("original_room_content_data")

        element_types = self._room_element_types()
        room_items = []
        for element_type in element_types:
            items = room_content_data[element_type]
            for it in items:
                it["element_type"] = element_type
            room_items.extend(items)

        if not self._include_ex_room_entities:
            # iterate over relevant element types and sub-select for in-room items, resetting room_content_data
            # a little inefficient, could be done in one for loop but this is more extendable
            room_items = [item for item in room_items if item[consts.IS_IN_ROOM]]
            for element_type in element_types:
                type_room_items = [
                    pl for pl in room_items if pl["element_type"] == element_type
                ]
                room_content_data[element_type] = type_room_items

        label, label_name, label_state_change = self.pick_label(
            room_items, room_content_data["setting"]
        )

        # re-set room_content with room_items, which may have had label item removed
        for element_type in element_types:
            type_room_items = [
                pl for pl in room_items if pl["element_type"] == element_type
            ]
            room_content_data[element_type] = type_room_items

        # Picking the label
        new_message.force_set(
            "labels", [replace_binarized_attributes_with_description(label)]
        )

        # Generating the example text. Note that we need to generate label
        # first because that removes the label from the message ontent.
        # TODO: handle drop out values (remember is_end_adding_example AND datatype)
        element_types = [
            consts.ElementType.ROOM,
            consts.ElementType.OBJECT,
            consts.ElementType.CHARACTER,
        ]
        # generate context of graph tuples, pass in label_state_change to be removed from context
        # remove_reference refers to whether this teacher wants to remove
        state_text = generate_graph_tuples(
            room_content_data,
            element_types,
            only_in_edges=not self._include_ex_room_entities,
            dropouts=self._text_features_droputs,
            label_tuples=set([label_state_change]),
            remove_reference=self.remove_endpoint_references(),
        )

        new_message.force_set(
            "text",
            self._delimiter.join(
                [
                    replace_binarized_attributes_with_description(state_text),
                    self.get_teacher_prompt(name=label_name),
                ]
            ),
        )
        return new_message


class AddObjectCharacterBase(RoomElementBase):
    """
    Base teacher for adding objects and characters, and their respective graph
    attributes.
    """

    @abstractmethod
    def type_relevant_dropouts(self):
        """
        Return all relevant dropouts for this type of item (e.g. wearing_do).

        This selection will be converted to 0 or 1 based on the goal features to limit
        the label's scope
        """

    @abstractmethod
    def get_goal_features(self):
        """
        Return the goal dropouts (as a set) from the label that this teacher should
        predict The output of this method should be a subset of the relevant_dropouts.
        """

    def generate_label_dropouts(self):
        # apply absolute dropout to every (relevant to this type) feature that isn't in the goal set
        # this allows us to select only for the features that we want to predict
        goal_dropout_features = self.get_goal_features()
        dropouts = copy.deepcopy(self._text_features_droputs)

        # these keys are dropouts that apply to an item's graph attributes
        for key in self.type_relevant_dropouts():
            # if this key is in the goal features, we always want to include it
            if key in goal_dropout_features:
                dropouts[key] = 0
            else:
                dropouts[key] = 1
        return dropouts

    def generate_element_graph_states(self, room_name, element):
        graph_state = []
        # To generate the graph state needed to add this single object,
        # we generate the graph for an empty room that only has this single object.

        single_element_room = {"setting": room_name, element["element_type"]: [element]}
        dropouts = self.generate_label_dropouts()
        if element["element_type"] == "objects":
            add_room_objects_to_graph_state(
                single_element_room,
                graph_state,
                # Because the object is already selected wrt self._include_ex_room_entities
                only_in_edges=False,
                dropouts=dropouts,
                dropout_default=1,
            )
        elif element["element_type"] == "characters":
            add_room_characters_to_graph_state(
                single_element_room,
                graph_state,
                # Because the object is already selected wrt self._include_ex_room_entities
                only_in_edges=False,
                dropouts=dropouts,
            )

        return graph_state


@register_teacher("light:common_sense:AddObjectTeacher")
class AddObjectTeacher(AddObjectCharacterBase):
    """
    Suggests a new object, given the room settings.

    Also serves as base teacher for further object teachers
    """

    def type_relevant_dropouts(self):
        return (
            consts.GraphDropoutOptions.OBJECT_TYPE,
            consts.GraphDropoutOptions.OBJECT_INSIDE_ROOM,
            consts.GraphDropoutOptions.CONTAINED_OBJECTS,
            consts.GraphDropoutOptions.PHYS_DESCRIPTION,
            consts.GraphDropoutOptions.OBJECT_IS_GETTABLE,
            consts.GraphDropoutOptions.OBJECT_IS_DRINK,
            consts.GraphDropoutOptions.OBJECT_IS_FOOD,
            consts.GraphDropoutOptions.OBJECT_IS_CONTAINER,
            consts.GraphDropoutOptions.OBJECT_IS_SURFACE,
            consts.GraphDropoutOptions.OBJECT_IS_WEAPON,
            consts.GraphDropoutOptions.OBJECT_IS_WEARABLE,
        )

    def get_id(self):
        return "AddObjectTeacher"

    def get_goal_features(self):
        return {
            consts.GraphDropoutOptions.OBJECT_INSIDE_ROOM,
        }

    def _room_element_types(self):
        return ["objects"]

    def get_teacher_prompt(self, name=""):
        return random.choice(consts.TEACHER_PROMPTS["adding_objects"])

    def remove_endpoint_references(self):
        return False


@register_teacher("light:common_sense:AddObjectContainsTeacher")
class AddObjectContainsTeacher(AddObjectTeacher):
    """
    Suggests what this object might contain, given the room settings.
    """

    def get_id(self):
        return "AddObjectContainsTeacher"

    def get_goal_features(self):
        return {consts.GraphDropoutOptions.CONTAINED_OBJECTS}

    def get_teacher_prompt(self, name=""):
        prompt = random.choice(consts.TEACHER_PROMPTS["adding_object_contains"])
        return prompt.format(name=name)

    def delete_label_item(self):
        return False

    def remove_endpoint_references(self):
        return True

    def select_from_available_mutations(self):
        return True


@register_teacher("light:common_sense:AddObjectDescriptionTeacher")
class AddObjectDescriptionTeacher(AddObjectTeacher):
    """
    Suggests what physical description this object might have, given the room settings.
    """

    def get_id(self):
        return "AddObjectDescriptionTeacher"

    def get_goal_features(self):
        return {consts.GraphDropoutOptions.PHYS_DESCRIPTION}

    def get_teacher_prompt(self, name=""):
        prompt = random.choice(consts.TEACHER_PROMPTS["adding_physical_description"])
        return prompt.format(name=name)

    def delete_label_item(self):
        return False

    def add_no_mutation_option(self):
        return False


@register_teacher("light:common_sense:AddCharacterTeacher")
class AddCharacterTeacher(AddObjectCharacterBase):
    """
    Suggests a new character, given the room settings.

    Also serves as base teacher for further character teachers
    """

    def type_relevant_dropouts(self):
        return [
            consts.GraphDropoutOptions.CHARACTER_TYPE,
            consts.GraphDropoutOptions.CHARACTER_INSIDE_ROOM,
            consts.GraphDropoutOptions.PERSONA,
            consts.GraphDropoutOptions.PHYS_DESCRIPTION,
            consts.GraphDropoutOptions.WORN_OBJECTS,
            consts.GraphDropoutOptions.WIELDED_OBJECTS,
            consts.GraphDropoutOptions.CARRYING_OBJECTS,
        ]

    def get_id(self):
        return "AddCharacterTeacher"

    def get_goal_features(self):
        return {
            consts.GraphDropoutOptions.CHARACTER_INSIDE_ROOM,
        }

    def _room_element_types(self):
        return ["characters"]

    def get_teacher_prompt(self, name=""):
        return random.choice(consts.TEACHER_PROMPTS["adding_characters"])


@register_teacher("light:common_sense:AddCharacterWielding")
class AddCharacterWieldingTeacher(AddCharacterTeacher):
    """
    Suggests what this character might wield, given the room settings.
    """

    def get_id(self):
        return "AddCharacterWieldingTeacher"

    def get_goal_features(self):
        return {consts.GraphDropoutOptions.WIELDED_OBJECTS}

    def get_teacher_prompt(self, name=""):
        prompt = random.choice(consts.TEACHER_PROMPTS["adding_character_wielding"])
        return prompt.format(name=name)

    def delete_label_item(self):
        return False

    def remove_endpoint_references(self):
        return True

    def select_from_available_mutations(self):
        return True


@register_teacher("light:common_sense:AddCharacterCarryingTeacher")
class AddCharacterCarryingTeacher(AddCharacterTeacher):
    """
    Suggests what this character might carry, given the room settings.
    """

    def get_id(self):
        return "AddCharacterCarryingTeacher"

    def get_goal_features(self):
        return {consts.GraphDropoutOptions.CARRYING_OBJECTS}

    def get_teacher_prompt(self, name=""):
        prompt = random.choice(consts.TEACHER_PROMPTS["adding_character_carrying"])
        return prompt.format(name=name)

    def delete_label_item(self):
        return False

    def remove_endpoint_references(self):
        return True

    def select_from_available_mutations(self):
        return True


@register_teacher("light:common_sense:AddCharacterWearingTeacher")
class AddCharacterWearingTeacher(AddCharacterTeacher):
    """
    Suggests what this character might wear, given the room settings.
    """

    def get_id(self):
        return "AddCharacterWearingTeacher"

    def get_goal_features(self):
        return {consts.GraphDropoutOptions.WORN_OBJECTS}

    def get_teacher_prompt(self, name=""):
        prompt = random.choice(consts.TEACHER_PROMPTS["adding_character_wearing"])
        return prompt.format(name=name)

    def delete_label_item(self):
        return False

    def remove_endpoint_references(self):
        return True

    def select_from_available_mutations(self):
        return True


@register_teacher("light:common_sense:AddCharacterDescriptionTeacher")
class AddCharacterDescriptionTeacher(AddCharacterTeacher):
    """
    Suggests what physical description this character might have, given the room
    settings.
    """

    def get_id(self):
        return "AddCharacterDescriptionTeacher"

    def get_goal_features(self):
        return {consts.GraphDropoutOptions.PHYS_DESCRIPTION}

    def get_teacher_prompt(self, name=""):
        prompt = random.choice(consts.TEACHER_PROMPTS["adding_physical_description"])
        return prompt.format(name=name)

    def delete_label_item(self):
        return False

    def add_no_mutation_option(self):
        return False


@register_teacher("light:common_sense:AddCharacterPersonaTeacher")
class AddCharacterPersonaTeacher(AddCharacterTeacher):
    """
    Suggests what persona this character might have, given the room settings.
    """

    def get_id(self):
        return "AddCharacterPersonaTeacher"

    def get_goal_features(self):
        return {consts.GraphDropoutOptions.PERSONA}

    def get_teacher_prompt(self, name=""):
        prompt = random.choice(consts.TEACHER_PROMPTS["adding_character_persona"])
        return prompt.format(name=name)

    def delete_label_item(self):
        return False

    def add_no_mutation_option(self):
        return False


@register_teacher("light:common_sense:AddItemTypeTeacher")
class AddItemTypeTeacher(AddObjectCharacterBase):
    """
    Suggests a new character, given the room settings.

    Also serves as base teacher for further character teachers
    """

    def type_relevant_dropouts(self):
        return [
            consts.GraphDropoutOptions.OBJECT_TYPE,
            consts.GraphDropoutOptions.OBJECT_INSIDE_ROOM,
            consts.GraphDropoutOptions.CONTAINED_OBJECTS,
            consts.GraphDropoutOptions.PHYS_DESCRIPTION,
            consts.GraphDropoutOptions.CHARACTER_TYPE,
            consts.GraphDropoutOptions.CHARACTER_INSIDE_ROOM,
            consts.GraphDropoutOptions.PERSONA,
            consts.GraphDropoutOptions.WORN_OBJECTS,
            consts.GraphDropoutOptions.WIELDED_OBJECTS,
            consts.GraphDropoutOptions.CARRYING_OBJECTS,
        ]

    def get_id(self):
        return "AddItemTypeTeacher"

    def get_goal_features(self):
        return {
            consts.GraphDropoutOptions.CHARACTER_TYPE,
            consts.GraphDropoutOptions.OBJECT_TYPE,
        }

    def _room_element_types(self):
        return ["objects", "characters"]

    def get_teacher_prompt(self, name=""):
        prompt = random.choice(consts.TEACHER_PROMPTS["add_item_type"])
        return prompt.format(name=name)

    def add_no_mutation_option(self):
        return False

    def remove_endpoint_references(self):
        return False

    def delete_label_item(self):
        return False


##################################################################################################
#
#               Common Sense QA teachers
#
##################################################################################################


class BaseCommonSenseQATeacher(RoomElementBase):
    def get_id(self):
        return "CommonSenseQATeacher"

    def add_no_mutation_select_buffer(self):
        return False

    def get_goal_features(self):
        return {self._goal_feature}


@register_teacher("light:common_sense:ObjectsCommonSenseQATeacher")
class ObjectsCommonSenseQATeacher(BaseCommonSenseQATeacher):

    OBJECT_ATTRIBUTES = (
        consts.GraphDropoutOptions.OBJECT_IS_GETTABLE,
        consts.GraphDropoutOptions.OBJECT_IS_DRINK,
        consts.GraphDropoutOptions.OBJECT_IS_FOOD,
        consts.GraphDropoutOptions.OBJECT_IS_CONTAINER,
        consts.GraphDropoutOptions.OBJECT_IS_SURFACE,
        consts.GraphDropoutOptions.OBJECT_IS_WEAPON,
        consts.GraphDropoutOptions.OBJECT_IS_WEARABLE,
    )

    def get_id(self):
        return "ObjectsCommonSenseQATeacher"

    def _room_element_types(self):
        return ["objects"]

    def type_relevant_dropouts(self):
        base_do_types = super().type_relevant_dropouts()
        base_do_types.extend(self.OBJECT_ATTRIBUTES)
        return base_do_types

    def get(self, episode_idx, entry_idx=0):
        # We use self._goal_feature in all the functions that we need to generate this example.
        self._goal_feature = random.choice(self.OBJECT_ATTRIBUTES)
        return super().get(episode_idx, entry_idx)

    def get_teacher_prompt(self, name):
        if self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_GETTABLE:
            prompt_type_key = "attribute_qa_gettable"
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_DRINK:
            prompt_type_key = "attribute_qa_drink"
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_FOOD:
            prompt_type_key = "attribute_qa_food"
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_CONTAINER:
            prompt_type_key = "attribute_qa_container"
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_SURFACE:
            prompt_type_key = "attribute_qa_surface"
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_WEAPON:
            prompt_type_key = "attribute_qa_weapon"
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_WEARABLE:
            prompt_type_key = "attribute_qa_wearable"
        else:
            raise ValueError(f"Unknown attribute {self._goal_feature}")

        prompt_template = random.choice(consts.TEACHER_PROMPTS[prompt_type_key])
        return prompt_template.format(name=name)

    def generate_element_graph_states(self, element):
        graph_state = []
        object_name = element["name"]

        if self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_GETTABLE:
            add_to_graph_state(
                graph_state,
                object_name,
                float_to_binary_str(element["is_gettable"]),
                consts.GraphEdges.IS_GETTABLE,
            )
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_DRINK:
            add_to_graph_state(
                graph_state,
                object_name,
                float_to_binary_str(element["is_drink"]),
                consts.GraphEdges.IS_DRINK,
            )
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_FOOD:
            add_to_graph_state(
                graph_state,
                object_name,
                float_to_binary_str(element["is_food"]),
                consts.GraphEdges.IS_FOOD,
            )
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_CONTAINER:
            add_to_graph_state(
                graph_state,
                object_name,
                float_to_binary_str(element["is_container"]),
                consts.GraphEdges.IS_CONTAINER,
            )
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_SURFACE:
            add_to_graph_state(
                graph_state,
                object_name,
                float_to_binary_str(element["is_surface"]),
                consts.GraphEdges.IS_SURFACE,
            )
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_WEAPON:
            add_to_graph_state(
                graph_state,
                object_name,
                float_to_binary_str(element["is_weapon"]),
                consts.GraphEdges.IS_WIELDABLE,
            )
        elif self._goal_feature == consts.GraphDropoutOptions.OBJECT_IS_WEARABLE:
            add_to_graph_state(
                graph_state,
                object_name,
                float_to_binary_str(element["is_wearable"]),
                consts.GraphEdges.IS_WEARABLE,
            )
        else:
            raise ValueError(f"Unknown attribute {self._goal_feature}")

        return graph_state

    def pick_label(self, potential_labels, room_name):
        # We use self._goal_feature later
        assert self._goal_feature
        assert (
            potential_labels
        ), "The potential objects for common sense QA can not be empty."

        label_index = random.choice(range(len(potential_labels)))
        label_item = potential_labels[label_index]
        label_name = label_item["name"]
        new_graph_states = self.generate_element_graph_states(label_item)
        label_graph_tuple = random.choice(new_graph_states)
        return (
            get_mutation(label_graph_tuple, consts.GraphMutations.ADD),
            label_name,
            label_graph_tuple,
        )


##################################################################################################
#
#               Actions common sense teachers
#
##################################################################################################


def get_item_class(item_data):
    if item_data["room"]:
        return consts.ElementType.ROOM
    elif item_data["object"]:
        return consts.ElementType.OBJECT
    elif item_data["agent"]:
        return consts.ElementType.CHARACTER
    else:
        raise ValueError(f"Invalid item type. Item details {item_data}")


class GameActionsBaseTeacher(CommonSenseBaseTeacher):
    """
    Common sense for world actions (Abstract class).
    """

    def __init__(self, opt, shared=None):
        opt = copy.deepcopy(opt)
        opt["datafile"] = self._get_datafile_path(opt)
        # `_no_mutation_label_do` is different from the rest because it is on the whole example,
        # not the components of the context. That's why we keep it seperate from others,
        # outside the `_text_features_droputs` dict.
        self._no_mutation_label_do = opt["no_mutation_label_do"]
        super().__init__(opt, shared)
        for k in (
            "dialog_history_do",
            "state_mutations_history_do",
            "object_info_do",
            "character_info_do",
            "character_context_do",
        ):
            self._text_features_droputs[k] = opt[k]

    def _keep_self_play_data(self):
        return False

    @classmethod
    def add_cmdline_args(cls, parser: ParlaiParser, partial_opt=None) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        arg_group = parser.add_argument_group("Common sense actions teacher arguments.")
        arg_group.add_argument(
            "--dialog-history-do",
            type=float,
            default=0,
            help=("The dropout rate for the dialogue history between the agents."),
        )
        arg_group.add_argument(
            "--state-mutations-history-do",
            type=float,
            default=0,
            help=("The dropout rate for the history of the game state changes."),
        )
        arg_group.add_argument(
            "--object-info-do",
            type=float,
            default=0,
            help=("The dropout rate for object info (eg, drinkable, wearable, etc.)."),
        )
        arg_group.add_argument(
            "--character-info-do",
            type=float,
            default=0,
            help=("The dropout rate for character info (eg, health, strength, etc.)."),
        )
        arg_group.add_argument(
            "--character-context-do",
            type=float,
            default=0,
            help=(
                "The dropout rate for context message shown to the playing character."
            ),
        )
        arg_group.add_argument(
            "--no-mutation-label-do",
            type=float,
            default=0,
            help=("The dropout rate for *examples* with NO_MUTATION label."),
        )
        return parser

    def _get_datafile_path(self, opt):
        dtype = get_dtype(opt)
        fname = f"processed_{dtype}_convs.jsonl"
        return os.path.join(
            opt["datapath"], consts.DATASET_DIR_NAME, consts.GAMEPLAY_DIR, fname
        )

    def load_dialog_data(self, data_path):
        logging.info(f"Loading dataset from {data_path}")
        with jsonlines.open(data_path, "r") as fin:
            return [line for line in fin]

    def format_hist_element(self, actor, action_type, time_diff, action_data):
        action_relation = f"{action_type.name} ({time_diff})"
        return graph_state_tuple(actor, action_data, action_relation)

    def get_graph_state_tuples(self, json_graph, dropouts, dropouts_default=0):
        """
        Generates game state tuples for the given state graph.
        """

        graph_state_tuples = []
        graph_dict = json.loads(json_graph)

        def add_item_to_graph(item_to_add):
            """
            Adds nodes to the dictionary by BFS traversal of nodes tree.
            """
            # Adding the item itself
            item_type = get_item_class(item_to_add)
            item_name = item_to_add["name"].lower()
            add_to_graph_state(
                graph_state_tuples, item_name, item_type.name, consts.GraphEdges.IS_TYPE
            )

            if item_type == consts.ElementType.ROOM:
                # Room description
                if survives_dropout(
                    dropouts.get(
                        consts.GraphDropoutOptions.ROOM_DESCRIPTION, dropouts_default
                    )
                ):
                    add_to_graph_state(
                        graph_state_tuples,
                        item_name,
                        item_to_add["desc"],
                        consts.GraphEdges.HAS_DESCRIPTION,
                    )

                # Room backstory
                if survives_dropout(
                    dropouts.get(
                        consts.GraphDropoutOptions.ROOM_BACKSTORY, dropouts_default
                    )
                ):
                    add_to_graph_state(
                        graph_state_tuples,
                        item_name,
                        item_to_add["extra_desc"],
                        consts.GraphEdges.HAS_BACKSTORY,
                    )
            elif item_type == consts.ElementType.OBJECT and survives_dropout(
                dropouts.get("object_info_do", dropouts_default)
            ):
                for qual, edge_type in (
                    ("gettable", consts.GraphEdges.IS_GETTABLE),
                    ("wearable", consts.GraphEdges.IS_WEARABLE),
                    ("wieldable", consts.GraphEdges.IS_WIELDABLE),
                ):
                    add_to_graph_state(
                        graph_state_tuples,
                        item_name,
                        str(int(item_to_add[qual])),
                        edge_type,
                    )
            elif item_type == consts.ElementType.CHARACTER and survives_dropout(
                dropouts.get("character_info_do", dropouts_default)
            ):
                for qual, edge_type in (
                    ("dead", consts.GraphEdges.IS_DEAD),
                    ("damage", consts.GraphEdges.HAS_DAMAGE_LEVEL),
                    ("health", consts.GraphEdges.HAS_HEALTH_LEVEL),
                    ("strength", consts.GraphEdges.HAS_STRENGTH_LEVEL),
                ):
                    add_to_graph_state(
                        graph_state_tuples,
                        item_name,
                        str(int(item_to_add[qual])),
                        edge_type,
                    )

            # Recursively adding the objects under a component
            for sub_comps in item_to_add["contained_nodes"]:
                sub_comp_node = graph_dict["nodes"][sub_comps]
                sub_com_name = sub_comp_node["name"].lower()
                if item_type == consts.ElementType.ROOM:
                    sub_com_type = get_item_class(sub_comp_node)
                    if (
                        sub_com_type == consts.ElementType.OBJECT
                        and not survives_dropout(
                            dropouts.get(
                                consts.GraphDropoutOptions.ROOM_OBJECTS,
                                dropouts_default,
                            )
                        )
                    ) or (
                        sub_com_type == consts.ElementType.CHARACTER
                        and not survives_dropout(
                            dropouts.get(
                                consts.GraphDropoutOptions.ROOM_CHARACTERS,
                                dropouts_default,
                            )
                        )
                    ):
                        # Dropping out this top level item dropout.
                        continue

                    # Adding only if survives the top level item dropout.
                    add_to_graph_state(
                        graph_state_tuples,
                        sub_com_name,
                        item_name,
                        consts.GraphEdges.IS_INSIDE,
                    )
                    add_item_to_graph(sub_comp_node)
                elif item_type == consts.ElementType.OBJECT:
                    add_to_graph_state(
                        graph_state_tuples,
                        sub_com_name,
                        item_name,
                        consts.GraphEdges.IS_INSIDE,
                    )
                    add_item_to_graph(sub_comp_node)
                else:  # Item belongs to a character
                    equipped_type = sub_comp_node.get("equipped")
                    if not equipped_type:
                        add_to_graph_state(
                            graph_state_tuples,
                            item_name,
                            sub_com_name,
                            consts.GraphEdges.IS_CARRYING,
                        )
                        add_item_to_graph(sub_comp_node)
                        continue

                    if equipped_type == "equip":
                        # Handling unclarified equipped items
                        assert (
                            sub_comp_node["wearable"] or sub_comp_node["wieldable"]
                        ), "Equipped unequipable item."
                        if sub_comp_node["wearable"] and sub_comp_node["wieldable"]:
                            equipped_type = "wear_wield"
                        elif sub_comp_node["wearable"]:
                            equipped_type = "wear"
                        elif sub_comp_node["wieldable"]:
                            equipped_type = "wield"

                    if equipped_type == "wear_wield":
                        if survives_dropout(
                            dropouts.get(
                                consts.GraphDropoutOptions.WIELDED_OBJECTS,
                                dropouts_default,
                            )
                        ) and survives_dropout(
                            dropouts.get(
                                consts.GraphDropoutOptions.WORN_OBJECTS,
                                dropouts_default,
                            )
                        ):
                            add_to_graph_state(
                                graph_state_tuples,
                                item_name,
                                sub_com_name,
                                consts.GraphEdges.IS_WEARING,
                            )
                            add_to_graph_state(
                                graph_state_tuples,
                                item_name,
                                sub_com_name,
                                consts.GraphEdges.IS_WIELDING,
                            )
                            add_item_to_graph(sub_comp_node)

                    elif equipped_type == "wear":
                        if survives_dropout(
                            dropouts.get(
                                consts.GraphDropoutOptions.WORN_OBJECTS,
                                dropouts_default,
                            )
                        ):
                            add_to_graph_state(
                                graph_state_tuples,
                                item_name,
                                sub_com_name,
                                consts.GraphEdges.IS_WEARING,
                            )
                            add_item_to_graph(sub_comp_node)
                    elif equipped_type == "wield":
                        if survives_dropout(
                            dropouts.get(
                                consts.GraphDropoutOptions.WIELDED_OBJECTS,
                                dropouts_default,
                            )
                        ):
                            add_to_graph_state(
                                graph_state_tuples,
                                item_name,
                                sub_com_name,
                                consts.GraphEdges.IS_WIELDING,
                            )
                            add_item_to_graph(sub_comp_node)
                    else:
                        ValueError(
                            f'Object with invalid equipped type "{equipped_type}".'
                        )

        rooms = graph_dict["rooms"]
        assert (
            len(rooms) == 1
        ), f"Common sense teacher is currently only handling one room."
        # Adding the room, and recursively anything underneath it.
        add_item_to_graph(graph_dict["nodes"][rooms[0]])
        return consts.GRAPH_STATES_DELIM.join(graph_state_tuples)

    def get_graph_diff(self, graph_1, graph_2):
        graph_1_tuples = set(graph_1.split(consts.GRAPH_STATES_DELIM))
        graph_2_tuples = set(graph_2.split(consts.GRAPH_STATES_DELIM))
        ret_diff = []

        for tuple_to_add in graph_1_tuples - graph_2_tuples:
            ret_diff.append(get_mutation(tuple_to_add, consts.GraphMutations.ADD))

        for tuple_to_del in graph_2_tuples - graph_1_tuples:
            ret_diff.append(get_mutation(tuple_to_del, consts.GraphMutations.DEL))

        return (
            consts.GRAPH_STATES_DELIM.join(ret_diff)
            if ret_diff
            else consts.GraphMutations.NO_MUTATION.name
        )

    def setup_data(self, datapath: str):
        dialog_data = self.load_dialog_data(datapath)

        # We keep all the data during setup.
        # Actual dropout happens when generating individual examples.
        NO_DROPOUTS_DICT = {}

        for convs in dialog_data:
            messages = []
            state_changes_hist = []
            for idx, conv in enumerate(convs):
                acting_agent = conv["speaker_id"]  # in each round agent acts and speaks
                speech_txt = conv["speech_text"].strip().replace("\n", " ")
                messages.append((idx, acting_agent, speech_txt))
                round_act = conv["action"]
                if not round_act:
                    continue
                act_message = Message(
                    {
                        "id": acting_agent,
                        # This is a proxy for marking event alogn the history.
                        "curr_time": idx,
                        # NOTE the hist lists are shared by the examples in an episode: the all keep
                        # a reference to the same list. We don't need to deep copy as long as we assure
                        # we process the length of the list that is relevant to that time-step.
                        "speech_hist": messages,
                        "world_changes_hist": state_changes_hist,
                        "action": round_act,
                        "agent_observation": conv["agent_observation"],
                        "player_context": conv["player_context"],
                        "possible_actions": conv["possible_actions"],
                        # We keep conv['game_state_after_action'] for applying dropout on it later
                        # By keeping the whole graph we assure that dropout happens correctly.
                        # For example, dropping out a character and all its related belongings.
                        "game_state_before_action": conv["game_state_before_action"],
                    }
                )

                graph_state_before_action = self.get_graph_state_tuples(
                    conv["game_state_before_action"],
                    dropouts=NO_DROPOUTS_DICT,
                )
                # We store this for keeing the correct order of the added entities.
                act_message[
                    "state_tuples_before_action"
                ] = graph_state_before_action.split(consts.GRAPH_STATES_DELIM)
                graph_state_after_action = self.get_graph_state_tuples(
                    conv["game_state_after_action"],
                    dropouts=NO_DROPOUTS_DICT,
                )
                graph_diff = self.get_graph_diff(
                    graph_state_after_action, graph_state_before_action
                )

                act_message["graph_diff"] = graph_diff
                if graph_diff != consts.GraphMutations.NO_MUTATION.name:
                    state_changes_hist.append(
                        (
                            idx,
                            acting_agent,
                            graph_diff.replace(
                                consts.GRAPH_STATES_DELIM,
                                consts.GRAPH_STATES_DELIM_HIST,
                            ),
                        )
                    )
                elif not survives_dropout(self._no_mutation_label_do):
                    # Skipping this example entirely
                    continue

                if (
                    self._keep_self_play_data()
                    and consts.ONE_LEVEL_SELF_PLAY_KEY in conv
                ):
                    # This part of the message will be processed during child calss setup
                    act_message[consts.ONE_LEVEL_SELF_PLAY_KEY] = conv[
                        consts.ONE_LEVEL_SELF_PLAY_KEY
                    ]

                yield act_message, True

    def _get_hist_txt_feature(self, example, example_feat_name, edge_type):
        curr_time_idx = example["curr_time"]
        message_hist_txt_parts = []
        for time_idx, sender, message in example[example_feat_name]:
            time_diff = curr_time_idx - time_idx
            if time_diff < 0:
                break
            message_hist_txt_parts.append(
                self.format_hist_element(sender, edge_type, time_diff, message)
            )
        return consts.GRAPH_STATES_DELIM.join(message_hist_txt_parts)

    def get_speech_hist_text_feature(self, example):
        return self._get_hist_txt_feature(
            example, "speech_hist", consts.GraphEdges.HAD_SAID
        )

    def get_world_change_hist_text_feature(self, example):
        return self._get_hist_txt_feature(
            example, "world_changes_hist", consts.GraphEdges.HAD_ACTED
        )

    def get(self, episode_idx, entry_idx=0):
        example = super().get(episode_idx, entry_idx)
        return Message(
            {
                "id": example["id"],
                "episode_done": True,
                "text": self._delimiter.join(
                    [
                        replace_binarized_attributes_with_description(
                            self.generate_example_text(example)
                        ),
                        self.get_teacher_prompt(example),
                    ]
                ),
                "labels": [
                    replace_binarized_attributes_with_description(
                        self.generate_example_label(example)
                    )
                ],
            }
        )


def action_teacher_prompt(example):
    prompt = random.choice(consts.TEACHER_PROMPTS["action_effects"])
    return prompt.format(actor=example["id"], act=example["action"])


def narration_teacher_prompt(example):
    prompt = random.choice(consts.TEACHER_PROMPTS["narration_after_action"])
    return prompt.format(actor=example["id"], act=example["action"])


@register_teacher("light:common_sense:GameActionsTeacher")
class GameActionsTeacher(GameActionsBaseTeacher):
    """
    Common sense for player actions.
    """

    def get_id(self):
        return "WorldActionsCommonSenseTeacher"

    def generate_example_text(self, example):

        txt_feature_parts = []

        # Adding the dialog history
        if survives_dropout(self._text_features_droputs["dialog_history_do"]):
            txt = self.get_speech_hist_text_feature(example)
            if txt:
                txt_feature_parts.append(txt)

        # Adding the action history
        if survives_dropout(self._text_features_droputs["state_mutations_history_do"]):
            txt = self.get_world_change_hist_text_feature(example)
            if txt:
                txt_feature_parts.append(txt)

        # We need to make sure `need_state_tuple` are not dropped out,
        # because the graph action changes these (deletes them after action).
        need_state_tuple_set = set()
        del_mutation_token = get_mutation_token(consts.GraphMutations.DEL)
        for mut in example["graph_diff"].split(consts.GRAPH_STATES_DELIM):
            if not mut.startswith(del_mutation_token):
                continue
            need_state_tuple_set.add(mut.replace(del_mutation_token, "").strip())

        # We generate two copies of graph states, one with dropout (A) and one without (B).
        # Then we check each tuple in B and add it to the output if it is in A or in the
        # graph mutations that are going to change based on the action (need_state_tuple_set).
        # Also note that because B doesn't chaneg due to dropout, we generate if once,
        # during setup, and store it with the example (`state_tuples_before_action`).
        init_states_with_do_set = set(
            self.get_graph_state_tuples(
                example["game_state_before_action"],
                dropouts=self._text_features_droputs,
            ).split(consts.GRAPH_STATES_DELIM)
        )

        # If we always add `need_state_tuple` to the end (or some random insertion point)
        # there are ways for the model to cheat based and find the out of place pattens of
        # the insertion point. By keeping the natural order of states between examples,
        # we avoid this. An alternative could be shuffling states everytime.
        # But it may make it harder for the model to learn (just a guess).
        ret_states = []
        states_to_keep = init_states_with_do_set.union(need_state_tuple_set)
        for cand_state in example["state_tuples_before_action"]:
            if cand_state in states_to_keep:
                ret_states.append(cand_state)

        if survives_dropout(self._text_features_droputs["character_context_do"]):
            ret_states.append(
                graph_state_tuple(
                    example["id"],
                    example["player_context"],
                    consts.GraphEdges.HAS_PLAYER_CONTEXT,
                )
            )

        txt_feature_parts.append(consts.GRAPH_STATES_DELIM.join(ret_states))

        return self._delimiter.join(txt_feature_parts)

    def generate_example_label(self, example):
        return example["graph_diff"]

    def get_teacher_prompt(self, example):
        return action_teacher_prompt(example)


def action_narration_tuple(example):
    return graph_state_tuple(
        example["id"], example["agent_observation"], consts.GraphEdges.OBSERVED
    )


@register_teacher("light:common_sense:GameActionsNarrationTeacher")
class GameActionsNarrationTeacher(GameActionsTeacher):
    def get_id(self):
        return "GameActionsNarration"

    def setup_data(self, datapath: str):
        for msg, _ in super().setup_data(datapath):
            if msg.get("agent_observation"):
                # skip rounds that there was no action from use and thus no observation.
                assert msg.get("action")
                yield msg, True

    def generate_example_label(self, example):
        return action_narration_tuple(example)

    def get_teacher_prompt(self, example):
        return narration_teacher_prompt(example)


@register_teacher("light:common_sense:SelfPlayTeacher")
class SelfPlayTeacher(GameActionsTeacher):
    """
    Agent observations after a potential action.
    """

    def __init__(self, opt, shared=None):
        self._data_size_reduction_factor = opt["selfplay_data_reduc_factor"]
        assert self._data_size_reduction_factor >= 1, "Minimum reduction factor is 1."
        super().__init__(opt, shared=shared)

    @classmethod
    def add_cmdline_args(cls, parser: ParlaiParser, partial_opt=None) -> ParlaiParser:
        super().add_cmdline_args(parser, partial_opt)
        arg_group = parser.add_argument_group(
            "LIGHT common sense self-play action teachers."
        )
        arg_group.add_argument(
            "--selfplay-data-reduc-factor",
            type=int,
            default=1,
            help=("To reduce the size of the dataset by this factor."),
        )
        return parser

    def _keep_self_play_data(self):
        return True

    def get_id(self):
        return "SelfPlayActions"

    def get_teacher_prompt(self, example):
        return action_teacher_prompt(example)

    def setup_data(self, datapath: str):
        for idx, (original_msg, _) in enumerate(super().setup_data(datapath)):
            if idx % self._data_size_reduction_factor > 0:
                continue

            action_roll_outs = original_msg.pop(consts.ONE_LEVEL_SELF_PLAY_KEY, None)
            if not action_roll_outs:
                continue

            del original_msg["possible_actions"]  # don't need it

            for act in action_roll_outs:
                message = copy.deepcopy(original_msg)
                for ovrds in ("action", "agent_observation"):
                    message.force_set(ovrds, act[ovrds])
                graph_state_before_action = consts.GRAPH_STATES_DELIM.join(
                    message["state_tuples_before_action"]
                )
                graph_state_after_action = self.get_graph_state_tuples(
                    act["game_state_after_action"],
                    dropouts={},
                )
                message.force_set(
                    "graph_diff",
                    self.get_graph_diff(
                        graph_state_after_action, graph_state_before_action
                    ),
                )
                yield message, True


@register_teacher("light:common_sense:SelfPlayNarrationTeacher")
class SelfPlayNarrationTeacher(SelfPlayTeacher):
    def get_id(self):
        return "SelfPlayActionsNarration"

    def generate_example_label(self, example):
        return action_narration_tuple(example)

    def get_teacher_prompt(self, example):
        return narration_teacher_prompt(example)
