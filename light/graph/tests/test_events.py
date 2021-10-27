#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import unittest
import json
import random
import copy
from light.graph.events.base import (
    ProcessedArguments,
    GraphEvent,
    ErrorEvent,
)
from light.graph.events.graph_events import (
    SayEvent,
    ShoutEvent,
    WhisperEvent,
    TellEvent,
    LeaveEvent,
    ArriveEvent,
    GoEvent,
    UnfollowEvent,
    FollowEvent,
    DeathEvent,
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
    ExamineEvent,
    EmoteEvent,
    WaitEvent,
    InventoryEvent,
    HealthEvent,
    LookEvent,
)

from light.graph.structured_graph import OOGraph
from light.graph.elements.graph_nodes import (
    GraphObject,
    GraphAgent,
)
from light.world.world import World

from typing import Tuple, List, Type, Optional


class GraphEventTests(unittest.TestCase):
    """
    This class contains the basic structure of a test for a GraphEvent.

    It requires specifying initial inputs and expected outputs.
    """

    INPUT_WORLD_JSON: str
    ERROR_CASES: List[Tuple[str, str]]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ]
    EVENT_CLASS: Type[GraphEvent]

    HAS_VALID_EVENTS = True

    @classmethod
    def setUpClass(cls):
        """
        Only run tests on subclasses of this class, as this class is just defining the
        testing interface and the tests to run for a graph event
        """
        if cls is GraphEventTests:
            raise unittest.SkipTest("Skip GraphEventTests tests, it's a base class")
        super(GraphEventTests, cls).setUpClass()

    def setUp(self) -> None:
        """
        Setup should put together any requirements for starting the database for a test.
        """
        self.world = World({}, None)
        self.reset_world()

    def reset_world(self) -> None:
        self.graph = OOGraph.from_json(self.INPUT_WORLD_JSON)
        self.world.oo_graph = self.graph
        random.seed(42)

    def test_run_successful_cases(self) -> None:
        """
        Try any tests that should result in successful outcomes.
        """
        GraphEventClass = self.EVENT_CLASS
        for (
            actor_id,
            input_string,
            found_node_ids,
            text,
            output_graph_json,
            observed_events,
        ) in self.SUCCESS_CASES:
            self.reset_world()
            actor_node = self.graph.get_node(actor_id)
            possible_text_args = GraphEventClass.split_text_args(
                actor_node, input_string
            )
            self.assertNotIsInstance(
                possible_text_args,
                ErrorEvent,
                f"Recieved error {possible_text_args} processing string on input {input_string}",
            )
            assert not isinstance(possible_text_args, ErrorEvent)
            found_success = False
            for string_args in possible_text_args:
                result = GraphEventClass.find_nodes_for_args(
                    self.graph, actor_node, *string_args
                )
                if isinstance(result, ErrorEvent):
                    continue
                found_success = True
                break
            self.assertTrue(
                found_success,
                f"Did not succesesfully find ProcessedArguments on input {input_string}, got {result}",
            )
            assert not isinstance(result, ErrorEvent)
            target_nodes = result.targets
            target_node_ids = [x.node_id for x in target_nodes]
            self.assertListEqual(
                target_node_ids,
                found_node_ids,
                f"Found target nodes {target_node_ids} not expected {found_node_ids}",
            )
            found_text = result.text
            self.assertEqual(
                text,
                found_text,
                f"Found text {found_text} was not expected text {text}",
            )
            event = GraphEventClass.construct_from_args(
                actor_node, target_nodes, found_text
            )
            self.assertIsInstance(
                event,
                GraphEventClass,
                f"Could not construct event on input {input_string}",
            )
            assert not isinstance(event, ErrorEvent)

            extra_events = event.execute(self.world)
            while len(extra_events) > 0:
                extra_event = extra_events.pop()
                extra_events.extend(extra_event.execute(self.world))
            res = event.to_json()
            before_oo_graph = copy.deepcopy(self.world.oo_graph)
            event_back = GraphEvent.from_json(res, self.world)
            self.assertEqual(
                type(event),
                type(event_back),
                "From Json event should be same type as base event",
            )
            class_ = event.__class__.__name__
            for k in event.__dict__:
                if not k.startswith(f"_{class_}__"):
                    self.assertEqual(
                        event.__dict__[k],
                        event_back.__dict__[k],
                        "From Json event should have the same k/v (except hidden vars):",
                    )
            self.graph = before_oo_graph
            self.world.oo_graph = self.graph
            self.graph.delete_nodes()
            final_json = self.world.oo_graph.to_json()
            self.assertDictEqual(
                json.loads(final_json.strip()),
                json.loads(output_graph_json.strip()),
                f"on input {input_string} Json not matching. : actual: {final_json.strip()}",
            )
            observations = actor_node.get_observations()
            observation_types = [type(x) for x in observations]
            self.assertListEqual(observation_types, observed_events)

    def test_run_error_cases(self) -> None:
        """
        Try any tests that should not result in unsuccessful outcomes.
        """
        GraphEventClass = self.EVENT_CLASS
        for (actor_id, input_string) in self.ERROR_CASES:
            self.reset_world()
            actor_node = self.graph.get_node(actor_id)
            possible_text_args = GraphEventClass.split_text_args(
                actor_node, input_string
            )
            if isinstance(possible_text_args, ErrorEvent):
                continue
            found_success = False
            success_event = None
            for string_args in possible_text_args:
                result = GraphEventClass.find_nodes_for_args(
                    self.graph, actor_node, *string_args
                )
                if isinstance(result, ErrorEvent):
                    continue
                else:
                    found_success = True
                    success_event = result
            if not found_success:
                continue
            assert isinstance(success_event, ProcessedArguments)
            target_nodes = success_event.targets
            found_text = success_event.text
            event = GraphEventClass.construct_from_args(
                actor_node, target_nodes, found_text
            )
            self.assertIsInstance(
                event,
                ErrorEvent,
                f"Successfully constructed event for bad input {input_string}",
            )

    def test_run_valid_cases(self) -> None:
        if not self.HAS_VALID_EVENTS:
            self.skipTest(f"No valid events for {self.EVENT_CLASS}")
        agent_ids = list(self.graph.agents.keys())
        GraphEventClass = self.EVENT_CLASS
        had_valid_test = False
        for agent_id in agent_ids:
            self.reset_world()
            actor_node = self.graph.get_node(agent_id)
            event_count = len(GraphEventClass.get_valid_actions(self.graph, actor_node))
            for e_idx in range(event_count):
                self.reset_world()
                actor_node = self.graph.get_node(agent_id)
                event = GraphEventClass.get_valid_actions(self.graph, actor_node)[e_idx]
                event.execute(self.world)
                _ = event.to_canonical_form()
                for viewer_id in agent_ids:
                    viewer = self.graph.get_node(viewer_id)
                    event_view = event.view_as(viewer)
                    if event_view is None:
                        continue
                    self.assertIsInstance(event_view, str)
                    self.assertTrue(len(event_view) > 0)

                # TODO run the world over the canonical action to show its the same
                # graph_dict = json.loads(self.graph.to_json())
                # self.reset_world()

                had_valid_test = True
        self.assertTrue(had_valid_test, "did not actually execute any valid cases")


test_graph_1 = """
{
    "agents": [
        "another_test_agent_2",
        "test_agent_0"
    ],
    "nodes": {
        "another_test_agent_2": {
            "agent": true,
            "aggression": 0,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {},
            "container_node": {
                "target_id": "base_room_1"
            },
            "db_id": null,
            "desc": "You really don't have a good reason to be examining this closer.",
            "followed_by": {},
            "following": null,
            "food_energy": 1,
            "health": 10,
            "is_player": false,
            "name": "another_test_agent",
            "name_prefix": "an",
            "names": [
                "another_test_agent"
            ],
            "node_id": "another_test_agent_2",
            "object": false,
            "persona": "I am a player in the LIGHT world.",
            "room": false,
            "size": 20,
            "speed": 0
        },
        "base_room_1": {
            "agent": false,
            "classes": [
                "room"
            ],
            "contain_size": 100000,
            "contained_nodes": {
                "another_test_agent_2": {
                    "target_id": "another_test_agent_2"
                },
                "test_agent_0": {
                    "target_id": "test_agent_0"
                }
            },
            "container_node": {
                "target_id": "VOID"
            },
            "db_id": null,
            "desc": "You try to get a better look, but it's just as non-descript",
            "extra_desc": "You try to get a better look, but it's just as non-descript",
            "name": "base_room",
            "name_prefix": "the",
            "names": [
                "base_room"
            ],
            "neighbors": {},
            "node_id": "base_room_1",
            "object": false,
            "room": true,
            "size": 1,
            "surface_type": "in"
        },
        "test_agent_0": {
            "agent": true,
            "aggression": 0,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {},
            "container_node": {
                "target_id": "base_room_1"
            },
            "db_id": null,
            "desc": "There's nothing special about it.",
            "followed_by": {},
            "following": null,
            "food_energy": 1,
            "health": 10,
            "is_player": false,
            "name": "test_agent",
            "name_prefix": "a",
            "names": [
                "test_agent"
            ],
            "node_id": "test_agent_0",
            "object": false,
            "persona": "I am a player in the LIGHT world.",
            "room": false,
            "size": 20,
            "speed": 0
        }
    },
    "objects": [],
    "rooms": [
        "base_room_1"
    ]
}
"""

test_graph_1_after_noop = OOGraph.from_json(test_graph_1).to_json()


class SayEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_1
    ERROR_CASES = [("test_agent_0", ""), ("test_agent_0", "\n")]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "test_agent_0",
            "something I'm giving up on you",
            [],
            "something I'm giving up on you",
            test_graph_1_after_noop,
            [SayEvent],
        ),
        (
            "test_agent_0",
            "this is a test phrase",
            [],
            "this is a test phrase",
            test_graph_1_after_noop,
            [SayEvent],
        ),
        (
            "test_agent_0",
            '"I can parse with quotations too"',
            [],
            "I can parse with quotations too",
            test_graph_1_after_noop,
            [SayEvent],
        ),
    ]
    EVENT_CLASS = SayEvent

    HAS_VALID_EVENTS = False


class ShoutEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_1
    ERROR_CASES = [("test_agent_0", ""), ("test_agent_0", "\n")]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "test_agent_0",
            "something I'm giving up on you",
            [],
            "something I'm giving up on you",
            test_graph_1_after_noop,
            [ShoutEvent],
        ),
        (
            "test_agent_0",
            "this is a test phrase",
            [],
            "this is a test phrase",
            test_graph_1_after_noop,
            [ShoutEvent],
        ),
        (
            "test_agent_0",
            '"I can parse with quotations too"',
            [],
            "I can parse with quotations too",
            test_graph_1_after_noop,
            [ShoutEvent],
        ),
    ]
    EVENT_CLASS = ShoutEvent

    HAS_VALID_EVENTS = False


class WhisperEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_1
    ERROR_CASES = [
        ("test_agent_0", ""),
        ("test_agent_0", "\n"),
        ("test_agent_0", "something I'm giving up on you"),
        ("test_agent_0", 'base_room "I can only parse with quotations"'),
        ("test_agent_0", 'another_test_agent "\n"'),
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "test_agent_0",
            'another_test_agent "I can only parse with quotations"',
            ["another_test_agent_2"],
            "I can only parse with quotations",
            test_graph_1_after_noop,
            [WhisperEvent],
        )
    ]
    EVENT_CLASS = WhisperEvent

    HAS_VALID_EVENTS = False


class TellEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_1
    ERROR_CASES = [
        ("test_agent_0", ""),
        ("test_agent_0", "\n"),
        ("test_agent_0", "something I'm giving up on you"),
        ("test_agent_0", 'base_room "I can only parse with quotations"'),
        ("test_agent_0", 'another_test_agent "\n"'),
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "test_agent_0",
            'another_test_agent "I can only parse with quotations"',
            ["another_test_agent_2"],
            "I can only parse with quotations",
            test_graph_1_after_noop,
            [TellEvent],
        )
    ]
    EVENT_CLASS = TellEvent

    HAS_VALID_EVENTS = False


test_graph_2 = """
{
    "agents": [
        "another_test_agent_2",
        "following_agent_0",
        "test_agent_0"
    ],
    "nodes": {
        "another_test_agent_2": {
            "agent": true,
            "aggression": 0,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {},
            "container_node": {
                "target_id": "base_room_1"
            },
            "db_id": null,
            "desc": "You really don't have a good reason to be examining this closer.",
            "defense": 100,
            "followed_by": {},
            "following": null,
            "food_energy": 1,
            "health": 10,
            "is_player": false,
            "name": "another_test_agent",
            "name_prefix": "an",
            "names": [
                "another_test_agent"
            ],
            "node_id": "another_test_agent_2",
            "object": false,
            "persona": "I am a player in the LIGHT world.",
            "room": false,
            "size": 20,
            "speed": 0
        },
        "base_room_1": {
            "agent": false,
            "classes": [
                "room"
            ],
            "contain_size": 100000,
            "contained_nodes": {
                "another_test_agent_2": {
                    "target_id": "another_test_agent_2"
                },
                "following_agent_0": {
                    "target_id": "following_agent_0"
                },
                "test_agent_0": {
                    "target_id": "test_agent_0"
                }
            },
            "container_node": {
                "target_id": "VOID"
            },
            "db_id": null,
            "desc": "You try to get a better look, but it's just as non-descript",
            "extra_desc": "You try to get a better look, but it's just as non-descript",
            "name": "base_room",
            "name_prefix": "the",
            "names": [
                "base_room"
            ],
            "neighbors": {
                "other_room_1": {
                    "examine_desc": "It's a path to the south",
                    "label": "south",
                    "locked_edge": null,
                    "target_id": "other_room_1"
                }
            },
            "node_id": "base_room_1",
            "object": false,
            "room": true,
            "size": 1,
            "surface_type": "in"
        },
        "following_agent_0": {
            "agent": true,
            "aggression": 0,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {},
            "container_node": {
                "target_id": "base_room_1"
            },
            "db_id": null,
            "desc": "There's nothing special about it.",
            "followed_by": {},
            "following": {
                "target_id": "test_agent_0"
            },
            "food_energy": 1,
            "health": 10,
            "movement_energy_cost": 0.05,
            "is_player": false,
            "name": "following_agent",
            "name_prefix": "a",
            "names": [
                "following_agent"
            ],
            "node_id": "following_agent_0",
            "object": false,
            "persona": "I am a player in the LIGHT world.",
            "room": false,
            "size": 20,
            "speed": 0
        },
        "other_room_1": {
            "agent": false,
            "classes": [
                "room"
            ],
            "contain_size": 100000,
            "contained_nodes": {},
            "container_node": {
                "target_id": "VOID"
            },
            "db_id": null,
            "desc": "There's nothing special about it.",
            "extra_desc": "There's nothing special about it.",
            "name": "other_room",
            "name_prefix": "the",
            "names": [
                "other_room"
            ],
            "neighbors": {
                "base_room_1": {
                    "examine_desc": "It's a path to the north",
                    "label": "north",
                    "locked_edge": null,
                    "target_id": "base_room_1"
                }
            },
            "node_id": "other_room_1",
            "object": false,
            "room": true,
            "size": 1,
            "surface_type": "in"
        },
        "test_agent_0": {
            "agent": true,
            "aggression": 0,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {},
            "container_node": {
                "target_id": "base_room_1"
            },
            "damage": 100,
            "db_id": null,
            "desc": "There's nothing special about it.",
            "followed_by": {
                "following_agent_0": {
                    "target_id": "following_agent_0"
                }
            },
            "following": null,
            "food_energy": 1,
            "health": 10,
            "movement_energy_cost": 0.05,
            "is_player": false,
            "name": "test_agent",
            "name_prefix": "a",
            "names": [
                "test_agent"
            ],
            "node_id": "test_agent_0",
            "object": false,
            "persona": "I am a player in the LIGHT world.",
            "room": false,
            "size": 20,
            "speed": 0
        }
    },
    "objects": [],
    "rooms": [
        "base_room_1",
        "other_room_1"
    ]
}
"""

test_graph_2_after_noop = OOGraph.from_json(test_graph_2).to_json()

test_graph_2_after_move_dict = json.loads(test_graph_2)
test_graph_2_after_move_dict["nodes"]["base_room_1"]["contained_nodes"] = {
    "another_test_agent_2": {"target_id": "another_test_agent_2"}
}
test_graph_2_after_move_dict["nodes"]["base_room_1"]["contain_size"] = 100040
test_graph_2_after_move_dict["nodes"]["other_room_1"]["contained_nodes"] = {
    "following_agent_0": {"target_id": "following_agent_0"},
    "test_agent_0": {"target_id": "test_agent_0"},
}
test_graph_2_after_move_dict["nodes"]["other_room_1"]["contain_size"] = 99960
test_graph_2_after_move_dict["nodes"]["following_agent_0"]["container_node"] = {
    "target_id": "other_room_1"
}
test_graph_2_after_move_dict["nodes"]["test_agent_0"]["container_node"] = {
    "target_id": "other_room_1"
}
test_graph_2_after_move_dict["nodes"]["test_agent_0"][
    "health"
] -= test_graph_2_after_move_dict["nodes"]["test_agent_0"]["movement_energy_cost"]
test_graph_2_after_move_dict["nodes"]["following_agent_0"][
    "health"
] -= test_graph_2_after_move_dict["nodes"]["following_agent_0"]["movement_energy_cost"]
test_graph_2_after_move = OOGraph.from_json(
    json.dumps(test_graph_2_after_move_dict)
).to_json()


class GoEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_2
    ERROR_CASES = [
        ("test_agent_0", "base_room"),
        ("test_agent_0", "following_agent"),
        ("test_agent_0", 'test_agent"'),
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "test_agent_0",
            "s",
            ["other_room_1"],
            None,
            test_graph_2_after_move,
            [LeaveEvent, ArriveEvent, LookEvent, ArriveEvent],
        ),
        (
            "test_agent_0",
            "south",
            ["other_room_1"],
            None,
            test_graph_2_after_move,
            [LeaveEvent, ArriveEvent, LookEvent, ArriveEvent],
        ),
    ]
    EVENT_CLASS = GoEvent


test_graph_2_after_follow_dict = json.loads(test_graph_2)
test_graph_2_after_follow_dict["nodes"]["another_test_agent_2"]["followed_by"] = {
    "following_agent_0": {"target_id": "following_agent_0"}
}
test_graph_2_after_follow_dict["nodes"]["following_agent_0"]["following"] = {
    "target_id": "another_test_agent_2"
}
test_graph_2_after_follow_dict["nodes"]["test_agent_0"]["followed_by"] = {}
test_graph_2_after_follow = OOGraph.from_json(
    json.dumps(test_graph_2_after_follow_dict)
).to_json()


class FollowEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_2
    ERROR_CASES = [
        ("following_agent_0", "test_agent"),  # Failed because already following them
        ("following_agent_0", "other_room"),  # Failed because not followable
        ("test_agent_0", ""),  # Failed because bad input
        ("test_agent_0", 'abc"'),  # Failed because not present
        (
            "another_test_agent_2",
            "another_test_agent",
        ),  # failed because can't follow self
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "following_agent_0",
            "another_test_agent",
            ["another_test_agent_2"],
            None,
            test_graph_2_after_follow,
            [UnfollowEvent, FollowEvent],
        )
    ]
    EVENT_CLASS = FollowEvent


test_graph_2_after_unfollow_dict = json.loads(test_graph_2)
test_graph_2_after_unfollow_dict["nodes"]["following_agent_0"]["following"] = None
test_graph_2_after_unfollow_dict["nodes"]["test_agent_0"]["followed_by"] = {}
test_graph_2_after_unfollow = OOGraph.from_json(
    json.dumps(test_graph_2_after_unfollow_dict)
).to_json()


class UnfollowEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_2
    ERROR_CASES = [("test_agent_0", "")]  # failed because not following
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "following_agent_0",
            "",
            [],
            None,
            test_graph_2_after_unfollow,
            [UnfollowEvent],
        )
    ]
    EVENT_CLASS = UnfollowEvent


test_graph_2_after_kill_following_dict = json.loads(test_graph_2)
del test_graph_2_after_kill_following_dict["nodes"]["following_agent_0"]
test_graph_2_after_kill_following_dict["nodes"]["following_agent_0__dead__"] = {
    "agent": False,
    "classes": ["object", "container", "agent"],
    "contain_size": 20,
    "contained_nodes": {},
    "container": True,
    "container_node": {"target_id": "base_room_1"},
    "db_id": None,
    "dead": True,
    "desc": "They look pretty dead.",
    "drink": False,
    "food": False,
    "food_energy": 1,
    "gettable": True,
    "locked_edge": None,
    "name": "following_agent",
    "name_prefix": "a",
    "names": ["following_agent"],
    "node_id": "following_agent_0__dead__",
    "object": True,
    "room": False,
    "size": 20,
    "stats": {"damage": 0, "defense": 0},
    "surface_type": "on",
    "value": 1,
    "wearable": False,
    "wieldable": False,
}
test_graph_2_after_kill_following_dict["nodes"]["test_agent_0"]["followed_by"] = {}
test_graph_2_after_kill_following_dict["nodes"]["base_room_1"]["contained_nodes"] = {
    "another_test_agent_2": {"target_id": "another_test_agent_2"},
    "following_agent_0__dead__": {"target_id": "following_agent_0__dead__"},
    "test_agent_0": {"target_id": "test_agent_0"},
}
test_graph_2_after_kill_following_dict["agents"] = [
    "another_test_agent_2",
    "test_agent_0",
]
test_graph_2_after_kill_following_dict["objects"] = ["following_agent_0__dead__"]
test_graph_2_after_kill_following = OOGraph.from_json(
    json.dumps(test_graph_2_after_kill_following_dict)
).to_json()


test_graph_2_after_hit_another_dict = json.loads(test_graph_2)
test_graph_2_after_hit_another_dict["nodes"]["test_agent_0"]["health"] = 8
test_graph_2_after_hit_another = OOGraph.from_json(
    json.dumps(test_graph_2_after_hit_another_dict)
).to_json()


class HitEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_2
    ERROR_CASES = [
        ("following_agent_0", "following_agent"),  # failed because can't hit self
        ("test_agent_0", "abc"),  # failed because bad input
        ("test_agent_0", ""),  # failed because no target
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "test_agent_0",
            "following_agent",
            ["following_agent_0"],
            None,
            test_graph_2_after_kill_following,
            [HitEvent, DeathEvent],
        ),
        (
            "following_agent_0",
            "another",
            ["another_test_agent_2"],
            None,
            test_graph_2_after_noop,
            [HitEvent],
        ),
        (
            "another_test_agent_2",
            "test",
            ["test_agent_0"],
            None,
            test_graph_2_after_hit_another,
            [HitEvent, HealthEvent],
        ),
    ]
    EVENT_CLASS = HitEvent


class HugEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_2
    ERROR_CASES = [
        ("following_agent_0", "following_agent"),  # failed because can't hug self
        ("test_agent_0", "abc"),  # failed because bad input
        ("test_agent_0", ""),  # failed because no target
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "test_agent_0",
            "following_agent",
            ["following_agent_0"],
            None,
            test_graph_2_after_noop,
            [HugEvent],
        ),
        (
            "following_agent_0",
            "another",
            ["another_test_agent_2"],
            None,
            test_graph_2_after_noop,
            [HugEvent],
        ),
        (
            "another_test_agent_2",
            "test",
            ["test_agent_0"],
            None,
            test_graph_2_after_noop,
            [HugEvent],
        ),
    ]
    EVENT_CLASS = HugEvent


class EmoteEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_2
    ERROR_CASES = [
        ("following_agent_0", "following_agent"),  # failed because this isn't an emote
        ("test_agent_0", "abc"),  # failed because not an emote
        ("test_agent_0", ""),  # failed because no target
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        ("test_agent_0", x, [], x, test_graph_2_after_noop, [EmoteEvent])
        for x in EmoteEvent.DESC_MAP.keys()
    ]
    EVENT_CLASS = EmoteEvent


class WaitEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_2
    ERROR_CASES: List[Tuple[str, str]] = [
        # Wait event cannot fail
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [("test_agent_0", "", [], None, test_graph_2_after_noop, [WaitEvent])]
    EVENT_CLASS = WaitEvent


class HealthEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_2
    ERROR_CASES: List[Tuple[str, str]] = [
        # Wait event cannot fail
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [("test_agent_0", "", [], None, test_graph_2_after_noop, [HealthEvent])]
    EVENT_CLASS = HealthEvent


test_graph_3 = OOGraph.from_json(
    """
{
    "agents": [
        "carrier_12",
        "trained_monkey_13",
        "sword_dealer_14"
    ],
    "nodes": {
        "carrier_12": {
            "agent": true,
            "aggression": 0,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {
                "sword_from_a_stone_4": {
                    "target_id": "sword_from_a_stone_4"
                },
                "hat_5": {
                    "target_id": "hat_5"
                },
                "poison_apple_8": {
                    "target_id": "poison_apple_8"
                },
                "tasty_steak_to_eat_9": {
                    "target_id": "tasty_steak_to_eat_9"
                },
                "goldfish_in_a_bag_11": {
                    "target_id": "goldfish_in_a_bag_11"
                },
                "something_to_drink_20": {
                    "target_id": "something_to_drink_20"
                }
            },
            "container_node": {
                "target_id": "main_room_0"
            },
            "db_id": null,
            "desc": "Someone who carries items for a test.",
            "followed_by": {},
            "following": null,
            "food_energy": 1,
            "health": 2,
            "is_player": false,
            "name": "carrier",
            "names": [
                "carrier"
            ],
            "node_id": "carrier_12",
            "object": false,
            "persona": "I am a carrier. I carry items and try to use them.",
            "room": false,
            "size": 20,
            "speed": 5
        },
        "trained_monkey_13": {
            "agent": true,
            "aggression": 0,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {},
            "container_node": {
                "target_id": "north_room_1"
            },
            "db_id": null,
            "desc": "A monkey that has been trained to test.",
            "followed_by": {},
            "following": null,
            "food_energy": 1,
            "health": 2,
            "is_player": false,
            "name": "trained monkey",
            "names": [
                "trained monkey"
            ],
            "node_id": "trained_monkey_13",
            "object": false,
            "persona": "I am a trained monkey. I am trained to test LIGHT.",
            "room": false,
            "size": 20,
            "speed": 5
        },
        "sword_dealer_14": {
            "agent": true,
            "dexterity": 1000,
            "aggression": 0,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {},
            "container_node": {
                "target_id": "main_room_0"
            },
            "db_id": null,
            "desc": "A person who deals swords.",
            "followed_by": {},
            "following": null,
            "food_energy": 1,
            "health": 2,
            "is_player": false,
            "name": "sword dealer",
            "names": [
                "sword dealer"
            ],
            "node_id": "sword_dealer_14",
            "object": false,
            "persona": "I am a sword dealer. I deal swords.",
            "room": false,
            "size": 20,
            "speed": 5
        },
        "main_room_0": {
            "agent": false,
            "classes": [
                "room"
            ],
            "contain_size": 2000,
            "contained_nodes": {
                "carrier_12": {
                    "target_id": "carrier_12"
                },
                "table_6": {
                    "target_id": "table_6"
                },
                "chest_7": {
                    "target_id": "chest_7"
                },
                "sword_dealer_14": {
                    "target_id": "sword_dealer_14"
                }
            },
            "container_node": {
                "target_id": "VOID"
            },
            "db_id": null,
            "desc": "A main room to be used in a test. Doesn't have any other interesting properties beyond that.",
            "extra_desc": "If you look very closely, you can observe testing as it occurs.",
            "name": "Main room",
            "name_prefix": "the",
            "names": [
                "Main room"
            ],
            "neighbors": {
                "north_room_1": {
                    "examine_desc": null,
                    "label": "north",
                    "locked_edge": null,
                    "target_id": "north_room_1"
                },
                "east_room_2": {
                    "examine_desc": null,
                    "label": "east",
                    "locked_edge": null,
                    "target_id": "east_room_2"
                }
            },
            "node_id": "main_room_0",
            "object": false,
            "room": true,
            "size": 2000,
            "surface_type": "in"
        },
        "sword_from_a_stone_4": {
            "agent": false,
            "classes": [
                "wieldable",
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "carrier_12"
            },
            "db_id": null,
            "desc": "This sword is good for slicing tests.",
            "drink": false,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "name": "sword from a stone",
            "names": [
                "sword from a stone"
            ],
            "node_id": "sword_from_a_stone_4",
            "object": true,
            "room": false,
            "size": 5,
            "stats": {
                "damage": 1
            },
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": true
        },
        "hat_5": {
            "agent": false,
            "classes": [
                "wearable",
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "carrier_12"
            },
            "db_id": null,
            "desc": "The hat has 'test' written across the front.",
            "drink": false,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "name": "hat",
            "names": [
                "hat"
            ],
            "node_id": "hat_5",
            "object": true,
            "room": false,
            "size": 1,
            "stats": {
                "defense": 1
            },
            "surface_type": "on",
            "value": 1,
            "wearable": true,
            "wieldable": false
        },
        "table_6": {
            "agent": false,
            "classes": [
                "container",
                "object"
            ],
            "contain_size": 3,
            "contained_nodes": {
                "contained_object_10": {
                    "target_id": "contained_object_10"
                }
            },
            "container": true,
            "container_node": {
                "target_id": "main_room_0"
            },
            "db_id": null,
            "desc": "The small table can't hold much more.",
            "drink": false,
            "food": false,
            "food_energy": 0,
            "gettable": false,
            "name": "table",
            "names": [
                "table"
            ],
            "node_id": "table_6",
            "object": true,
            "room": false,
            "size": 1,
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "chest_7": {
            "agent": false,
            "classes": [
                "container",
                "object"
            ],
            "contain_size": 10,
            "contained_nodes": {},
            "container": true,
            "container_node": {
                "target_id": "main_room_0"
            },
            "db_id": null,
            "desc": "The large chest starts empty for tests.",
            "drink": false,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "name": "chest",
            "names": [
                "chest"
            ],
            "node_id": "chest_7",
            "object": true,
            "room": false,
            "size": 1,
            "surface_type": "in",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "north_room_1": {
            "agent": false,
            "classes": [
                "room"
            ],
            "contain_size": 2000,
            "contained_nodes": {
                "trained_monkey_13": {
                    "target_id": "trained_monkey_13"
                }
            },
            "container_node": {
                "target_id": "VOID"
            },
            "db_id": null,
            "desc": "A north room to be used in a test. Doesn't have any other interesting properties beyond that.",
            "extra_desc": "If you look very closely, you can observe that nothing is here.",
            "name": "north room",
            "name_prefix": "the",
            "names": [
                "north room"
            ],
            "neighbors": {
                "main_room_0": {
                    "examine_desc": null,
                    "label": "south",
                    "locked_edge": null,
                    "target_id": "main_room_0"
                }
            },
            "node_id": "north_room_1",
            "object": false,
            "room": true,
            "size": 2000,
            "surface_type": "in"
        },
        "east_room_2": {
            "agent": false,
            "classes": [
                "room"
            ],
            "contain_size": 2000,
            "contained_nodes": {},
            "container_node": {
                "target_id": "VOID"
            },
            "db_id": null,
            "desc": "A east room to be used in a test. Doesn't have any other interesting properties beyond that.",
            "extra_desc": "If you look very closely, you can observe that nothing is here.",
            "name": "east room",
            "name_prefix": "the",
            "names": [
                "east room"
            ],
            "neighbors": {
                "main_room_0": {
                    "examine_desc": null,
                    "label": "west",
                    "locked_edge": null,
                    "target_id": "main_room_0"
                }
            },
            "node_id": "east_room_2",
            "object": false,
            "room": true,
            "size": 2000,
            "surface_type": "in"
        },
        "poison_apple_8": {
            "agent": false,
            "classes": [
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "carrier_12"
            },
            "db_id": null,
            "desc": "This apple is clearly poisoned.",
            "drink": false,
            "food": true,
            "food_energy": -15,
            "gettable": true,
            "name": "poison apple",
            "names": [
                "poison apple"
            ],
            "node_id": "poison_apple_8",
            "object": true,
            "room": false,
            "size": 1,
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "tasty_steak_to_eat_9": {
            "agent": false,
            "classes": [
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "carrier_12"
            },
            "db_id": null,
            "desc": "This steak looks delicious.",
            "drink": false,
            "food": true,
            "food_energy": 20,
            "gettable": true,
            "name": "tasty steak to eat",
            "names": [
                "tasty steak to eat"
            ],
            "node_id": "tasty_steak_to_eat_9",
            "object": true,
            "room": false,
            "size": 1,
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "contained_object_10": {
            "agent": false,
            "classes": [
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "table_6"
            },
            "db_id": null,
            "desc": "This object is contained.",
            "drink": false,
            "food": true,
            "food_energy": 0,
            "gettable": true,
            "name": "contained object",
            "names": [
                "contained object"
            ],
            "node_id": "contained_object_10",
            "object": true,
            "room": false,
            "size": 1,
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "goldfish_in_a_bag_11": {
            "agent": false,
            "classes": [
                "object"
            ],
            "contain_size": 5,
            "contained_nodes": {},
            "container": true,
            "container_node": {
                "target_id": "carrier_12"
            },
            "db_id": null,
            "desc": "There's a goldfish swimming around in this little bag.",
            "drink": false,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "name": "goldfish in a bag",
            "names": [
                "goldfish in a bag"
            ],
            "node_id": "goldfish_in_a_bag_11",
            "object": true,
            "room": false,
            "size": 1,
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "something_to_drink_20": {
            "agent": false,
            "classes": [
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "carrier_12"
            },
            "db_id": null,
            "desc": "This apple is clearly poisoned.",
            "drink": true,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "name": "something to drink",
            "names": [
                "something to drink"
            ],
            "node_id": "something_to_drink_20",
            "object": true,
            "room": false,
            "size": 1,
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        }
    },
    "objects": [
        "sword_from_a_stone_4",
        "hat_5",
        "table_6",
        "chest_7",
        "poison_apple_8",
        "tasty_steak_to_eat_9",
        "contained_object_10",
        "goldfish_in_a_bag_11",
        "something_to_drink_20"
    ],
    "rooms": [
        "main_room_0",
        "north_room_1",
        "east_room_2"
    ]
}
"""
).to_json()


class InventoryEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        # Inventory event cannot fail
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        # Test having a lot of items
        ("carrier_12", "", [], None, test_graph_3, [InventoryEvent]),
        # Test having nothing
        ("trained_monkey_13", "", [], None, test_graph_3, [InventoryEvent]),
        ("sword_dealer_14", "", [], None, test_graph_3, [InventoryEvent]),
    ]
    EVENT_CLASS = InventoryEvent


class LookEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        # Inventory event cannot fail
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        # Test having a lot of items
        ("carrier_12", "", [], None, test_graph_3, [LookEvent]),
        # Test having nothing
        ("trained_monkey_13", "", [], None, test_graph_3, [LookEvent]),
        ("sword_dealer_14", "", [], None, test_graph_3, [LookEvent]),
    ]
    EVENT_CLASS = LookEvent


# TODO test TriggeredEvents that aren't triggered by other events
class SpawnEventTest:
    pass


class ExamineEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        # Examine events fail if things can't be seen
        ("carrier_12", "contained object"),  # Can't examine things in things
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("carrier_12", "carrier"),
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "sword f",
            ["sword_from_a_stone_4"],
            None,
            test_graph_3,
            [ExamineEvent],
        ),
        (
            "carrier_12",
            "sword d",
            ["sword_dealer_14"],
            None,
            test_graph_3,
            [ExamineEvent],
        ),
        (
            "carrier_12",
            "sword",
            ["sword_dealer_14"],
            None,
            test_graph_3,
            [ExamineEvent],
        ),
        ("carrier_12", "room", ["main_room_0"], None, test_graph_3, [ExamineEvent]),
        (
            "trained_monkey_13",
            "south",
            ["main_room_0"],
            None,
            test_graph_3,
            [ExamineEvent],
        ),
        (
            "sword_dealer_14",
            "carrier",
            ["carrier_12"],
            None,
            test_graph_3,
            [ExamineEvent],
        ),
    ]
    EVENT_CLASS = ExamineEvent


test_graph_3_before_get_contained = OOGraph.from_json(test_graph_3)
contained_node = test_graph_3_before_get_contained.get_node("contained_object_10")
carrier_node = test_graph_3_before_get_contained.get_node("carrier_12")
assert contained_node is not None and carrier_node is not None, "Graph parsing failed"
contained_node.move_to(carrier_node)
test_graph_3_after_get_contained = test_graph_3_before_get_contained.to_json()

test_graph_3_before_get_chest = OOGraph.from_json(test_graph_3)
chest_node = test_graph_3_before_get_chest.get_node("chest_7")
carrier_node = test_graph_3_before_get_chest.get_node("carrier_12")
assert chest_node is not None and carrier_node is not None, "Graph parsing failed"
chest_node.move_to(carrier_node)
test_graph_3_after_get_chest = test_graph_3_before_get_chest.to_json()


class GetObjectEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("carrier_12", "contained object"),  # Must specify where to get from
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("carrier_12", "carrier"),  # Can't get self
        ("carrier_12", "sword from a stone"),  # Can't get something you already have
        ("carrier_12", "table"),  # Can't get things that aren't gettable
        ("carrier_12", "sword dealer"),  # Can't get people
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "contained from table",
            ["contained_object_10", "table_6"],
            None,
            test_graph_3_after_get_contained,
            [GetObjectEvent],
        ),
        (
            "carrier_12",
            "chest",
            ["chest_7", "main_room_0"],
            None,
            test_graph_3_after_get_chest,
            [GetObjectEvent],
        ),
    ]
    EVENT_CLASS = GetObjectEvent


test_graph_3_before_put_sword = OOGraph.from_json(test_graph_3)
contained_node = test_graph_3_before_put_sword.get_node("sword_from_a_stone_4")
chest_node = test_graph_3_before_put_sword.get_node("chest_7")
assert contained_node is not None and chest_node is not None, "Graph parsing failed"
contained_node.move_to(chest_node)
test_graph_3_after_put_sword = test_graph_3_before_put_sword.to_json()


class PutObjectInEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("carrier_12", "contained object"),  # Must specify where to put on/in
        ("carrier_12", "123 on 456"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("carrier_12", "carrier on table"),  # Can't put self
        ("carrier_12", "sword from a stone on table"),  # Can't overfill something
        ("carrier_12", "table in chest"),  # Can't put things you don't have
        ("carrier_12", "bag in bag"),  # Can't put things into themselves
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "sword from a stone in chest",
            ["sword_from_a_stone_4", "chest_7"],
            None,
            test_graph_3_after_put_sword,
            [PutObjectInEvent],
        ),
        (
            "carrier_12",
            "sword from a stone into chest",
            ["sword_from_a_stone_4", "chest_7"],
            None,
            test_graph_3_after_put_sword,
            [PutObjectInEvent],
        ),
    ]
    EVENT_CLASS = PutObjectInEvent


test_graph_3_before_drop_sword = OOGraph.from_json(test_graph_3)
contained_node = test_graph_3_before_drop_sword.get_node("sword_from_a_stone_4")
room_node = test_graph_3_before_drop_sword.get_node("main_room_0")
assert contained_node is not None and room_node is not None, "Graph parsing failed"
contained_node.move_to(room_node)
test_graph_3_after_drop_sword = test_graph_3_before_drop_sword.to_json()


class DropObjectEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("carrier_12", "contained object"),  # Can't drop what you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("carrier_12", "carrier"),  # Can't drop self
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "sword from a stone",
            ["sword_from_a_stone_4"],
            None,
            test_graph_3_after_drop_sword,
            [DropObjectEvent],
        ),
        (
            "carrier_12",
            "sword from a stone",
            ["sword_from_a_stone_4"],
            None,
            test_graph_3_after_drop_sword,
            [DropObjectEvent],
        ),
    ]
    EVENT_CLASS = DropObjectEvent


test_graph_3_before_steal_sword = OOGraph.from_json(test_graph_3)
contained_node = test_graph_3_before_steal_sword.get_node("sword_from_a_stone_4")
dealer_node = test_graph_3_before_steal_sword.get_node("sword_dealer_14")
assert contained_node is not None and dealer_node is not None, "Graph parsing failed"
contained_node.move_to(dealer_node)
test_graph_3_after_steal_sword = test_graph_3_before_steal_sword.to_json()


class StealObjectEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("carrier_12", "contained object"),  # Must specify where to steal from
        ("carrier_12", "123 from 456"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("carrier_12", "sword from sword dealer"),  # Can't steal something you have
        ("carrier_12", "sword from carrier"),  # Can't steal from self
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "sword_dealer_14",
            "sword from carrier",
            ["sword_from_a_stone_4", "carrier_12"],
            None,
            test_graph_3_after_steal_sword,
            [StealObjectEvent],
        ),
        (
            "sword_dealer_14",
            "sword from a stone from carrier",
            ["sword_from_a_stone_4", "carrier_12"],
            None,
            test_graph_3_after_steal_sword,
            [StealObjectEvent],
        ),
    ]
    EVENT_CLASS = StealObjectEvent


class GiveObjectEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("carrier_12", "sword"),  # Must specify where to give to
        ("carrier_12", "123 from 456"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "sword to carrier"),  # Can't give something you don't have
        ("carrier_12", "sword to carrier"),  # Can't give to self
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "sword from a stone to sword dealer",
            ["sword_from_a_stone_4", "sword_dealer_14"],
            None,
            test_graph_3_after_steal_sword,
            [GiveObjectEvent],
        ),
        (
            "carrier_12",
            "sword to sword",
            ["sword_from_a_stone_4", "sword_dealer_14"],
            None,
            test_graph_3_after_steal_sword,
            [GiveObjectEvent],
        ),
    ]
    EVENT_CLASS = GiveObjectEvent


test_graph_3_before_equip_sword = OOGraph.from_json(test_graph_3)

equipped_node = test_graph_3_before_equip_sword.get_node("sword_from_a_stone_4")
actor_node = test_graph_3_before_equip_sword.get_node("carrier_12")
assert isinstance(equipped_node, GraphObject), "Graph parsing failed"
assert isinstance(actor_node, GraphAgent), "Graph parsing failed"
equipped_node.equipped = 'equip'
actor_node.damage += 1
actor_node.num_wieldable_items = 1
actor_node.num_wearable_items = 0
test_graph_3_after_equip_sword = test_graph_3_before_equip_sword.to_json()

equipped_node = test_graph_3_before_equip_sword.get_node("hat_5")
assert isinstance(equipped_node, GraphObject), "Graph parsing failed"
equipped_node.equipped = 'equip'
actor_node.defense += 1
actor_node.num_wieldable_items = 1
actor_node.num_wearable_items = 1
test_graph_3_after_equip_both = test_graph_3_before_equip_sword.to_json()

test_graph_3_before_equip_hat = OOGraph.from_json(test_graph_3)
equipped_node = test_graph_3_before_equip_hat.get_node("hat_5")
actor_node = test_graph_3_before_equip_hat.get_node("carrier_12")
assert isinstance(equipped_node, GraphObject), "Graph parsing failed"
assert isinstance(actor_node, GraphAgent), "Graph parsing failed"
equipped_node.equipped = 'equip'
actor_node.defense += 1
actor_node.num_wieldable_items = 0
actor_node.num_wearable_items = 1
test_graph_3_after_equip_hat = test_graph_3_before_equip_hat.to_json()


class EquipObjectEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("sword_dealer_14", "chest"),  # Cant equip things you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "carrier"),  # Can't equip people
        ("carrier_12", "carrier"),  # Can't equip to self
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "sword from a stone",
            ["sword_from_a_stone_4"],
            None,
            test_graph_3_after_equip_sword,
            [EquipObjectEvent],
        ),
        (
            "carrier_12",
            "sword",
            ["sword_from_a_stone_4"],
            None,
            test_graph_3_after_equip_sword,
            [EquipObjectEvent],
        ),
        (
            "carrier_12",
            "hat",
            ["hat_5"],
            None,
            test_graph_3_after_equip_hat,
            [EquipObjectEvent],
        ),
    ]
    EVENT_CLASS = EquipObjectEvent

test_graph_3_before_wearing_hat = OOGraph.from_json(test_graph_3)
actor_node = test_graph_3_before_wearing_hat.get_node("carrier_12")
equipped_node = test_graph_3_before_wearing_hat.get_node("hat_5")
assert isinstance(equipped_node, GraphObject), "Graph parsing failed"
equipped_node.equipped = 'wear'
actor_node.defense += 1
actor_node.num_wieldable_items = 0
actor_node.num_wearable_items = 1
test_graph_3_after_wearing_hat = test_graph_3_before_wearing_hat.to_json()


class WearEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("sword_dealer_14", "chest"),  # Cant equip things you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "carrier"),  # Can't equip people
        ("carrier_12", "carrier"),  # Can't equip to self
        ("carrier_12", "sword from a stone"),  # Can't wear weapons
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "hat",
            ["hat_5"],
            None,
            test_graph_3_after_wearing_hat,
            [WearEvent],
        )
    ]
    EVENT_CLASS = WearEvent


class RemovenWearingObjectEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3_after_wearing_hat
    ERROR_CASES: List[Tuple[str, str]] = [
        ("sword_dealer_14", "chest"),  # Cant equip things you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "carrier"),  # Can't equip people
        ("carrier_12", "carrier"),  # Can't equip to self
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "hat",
            ["hat_5"],
            None,
            test_graph_3,
            [RemoveObjectEvent],
        ),
    ]
    EVENT_CLASS = RemoveObjectEvent


test_graph_3_before_wield_sword = OOGraph.from_json(test_graph_3)
equipped_node = test_graph_3_before_wield_sword.get_node("sword_from_a_stone_4")
actor_node = test_graph_3_before_wield_sword.get_node("carrier_12")
assert isinstance(equipped_node, GraphObject), "Graph parsing failed"
assert isinstance(actor_node, GraphAgent), "Graph parsing failed"
equipped_node.equipped = 'wield'
actor_node.damage += 1
actor_node.num_wieldable_items = 1
actor_node.num_wearable_items = 0
test_graph_3_after_wield_sword = test_graph_3_before_wield_sword.to_json()


class WieldEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("sword_dealer_14", "chest"),  # Cant equip things you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "carrier"),  # Can't equip people
        ("carrier_12", "carrier"),  # Can't equip to self
        ("carrier_12", "hat"),  # can't wield wearables
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "sword from a stone",
            ["sword_from_a_stone_4"],
            None,
            test_graph_3_after_wield_sword,
            [WieldEvent],
        ),
        (
            "carrier_12",
            "sword",
            ["sword_from_a_stone_4"],
            None,
            test_graph_3_after_wield_sword,
            [WieldEvent],
        ),
    ]
    EVENT_CLASS = WieldEvent


class RemovenWieldingObjectEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3_after_wield_sword
    ERROR_CASES: List[Tuple[str, str]] = [
        ("sword_dealer_14", "chest"),  # Cant equip things you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "carrier"),  # Can't equip people
        ("carrier_12", "carrier"),  # Can't equip to self
        ("carrier_12", "hat"),  # can't wield wearables
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "sword from a stone",
            ["sword_from_a_stone_4"],
            None,
            test_graph_3,
            [RemoveObjectEvent],
        ),
    ]
    EVENT_CLASS = RemoveObjectEvent


class RemoveObjectEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3_after_equip_both
    ERROR_CASES: List[Tuple[str, str]] = [
        ("sword_dealer_14", "chest"),  # Cant remove things you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "carrier"),  # Can't remove people
        ("carrier_12", "carrier"),  # Can't remove people
        ("carrier_12", "bag"),  # Can't remove things not equipped
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "sword",
            ["sword_from_a_stone_4"],
            None,
            test_graph_3_after_equip_hat,
            [RemoveObjectEvent],
        ),
        (
            "carrier_12",
            "hat",
            ["hat_5"],
            None,
            test_graph_3_after_equip_sword,
            [RemoveObjectEvent],
        ),
    ]
    EVENT_CLASS = RemoveObjectEvent


test_graph_3_before_ingest_steak_dict = json.loads(test_graph_3)
del test_graph_3_before_ingest_steak_dict["nodes"]["tasty_steak_to_eat_9"]
del test_graph_3_before_ingest_steak_dict["nodes"]["carrier_12"]["contained_nodes"][
    "tasty_steak_to_eat_9"
]
test_graph_3_before_ingest_steak_dict["nodes"]["carrier_12"]["contain_size"] += 1
test_graph_3_before_ingest_steak_dict["nodes"]["carrier_12"]["health"] = 22
test_graph_3_before_ingest_steak_dict["objects"].remove("tasty_steak_to_eat_9")
test_graph_3_after_ingest_steak = OOGraph.from_json(
    json.dumps(test_graph_3_before_ingest_steak_dict)
).to_json()

test_graph_3_after_ingest_apple = """
{
    "agents": [
        "sword_dealer_14",
        "trained_monkey_13"
    ],
    "nodes": {
        "carrier_12__dead__": {
            "agent": false,
            "classes": [
                "agent",
                "container",
                "object"
            ],
            "contain_size": 21,
            "contained_nodes": {
                "goldfish_in_a_bag_11": {
                    "target_id": "goldfish_in_a_bag_11"
                },
                "hat_5": {
                    "target_id": "hat_5"
                },
                "something_to_drink_20": {
                    "target_id": "something_to_drink_20"
                },
                "sword_from_a_stone_4": {
                    "target_id": "sword_from_a_stone_4"
                },
                "tasty_steak_to_eat_9": {
                    "target_id": "tasty_steak_to_eat_9"
                }
            },
            "container": true,
            "container_node": {
                "target_id": "main_room_0"
            },
            "db_id": null,
            "dead": true,
            "desc": "Their corpse is inanimate.",
            "drink": false,
            "equipped": null,
            "food": false,
            "food_energy": 1,
            "gettable": true,
            "locked_edge": null,
            "name": "carrier",
            "name_prefix": "the",
            "names": [
                "carrier"
            ],
            "node_id": "carrier_12__dead__",
            "object": true,
            "on_use": null,
            "room": false,
            "size": 21,
            "stats": {
                "damage": 0,
                "defense": 0
            },
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "chest_7": {
            "agent": false,
            "classes": [
                "container",
                "object"
            ],
            "contain_size": 10,
            "contained_nodes": {},
            "container": true,
            "container_node": {
                "target_id": "main_room_0"
            },
            "db_id": null,
            "dead": false,
            "desc": "The large chest starts empty for tests.",
            "drink": false,
            "equipped": null,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "locked_edge": null,
            "name": "chest",
            "name_prefix": "a",
            "names": [
                "chest"
            ],
            "node_id": "chest_7",
            "object": true,
            "on_use": null,
            "room": false,
            "size": 10,
            "stats": {
                "damage": 0,
                "defense": 0
            },
            "surface_type": "in",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "contained_object_10": {
            "agent": false,
            "classes": [
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "table_6"
            },
            "db_id": null,
            "dead": false,
            "desc": "This object is contained.",
            "drink": false,
            "equipped": null,
            "food": true,
            "food_energy": 0,
            "gettable": true,
            "locked_edge": null,
            "name": "contained object",
            "name_prefix": "a",
            "names": [
                "contained object"
            ],
            "node_id": "contained_object_10",
            "object": true,
            "on_use": null,
            "room": false,
            "size": 1,
            "stats": {
                "damage": 0,
                "defense": 0
            },
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "east_room_2": {
            "agent": false,
            "classes": [
                "room"
            ],
            "contain_size": 2000,
            "contained_nodes": {},
            "container_node": {
                "target_id": "VOID"
            },
            "db_id": null,
            "desc": "A east room to be used in a test. Doesn't have any other interesting properties beyond that.",
            "extra_desc": "If you look very closely, you can observe that nothing is here.",
            "grid_location": [
                0,
                0,
                0
            ],
            "name": "east room",
            "name_prefix": "the",
            "names": [
                "east room"
            ],
            "neighbors": {
                "main_room_0": {
                    "examine_desc": null,
                    "label": "west",
                    "locked_edge": null,
                    "target_id": "main_room_0"
                }
            },
            "node_id": "east_room_2",
            "object": false,
            "room": true,
            "size": 2000,
            "surface_type": "in"
        },
        "goldfish_in_a_bag_11": {
            "agent": false,
            "classes": [
                "object"
            ],
            "contain_size": 5,
            "contained_nodes": {},
            "container": true,
            "container_node": {
                "target_id": "carrier_12__dead__"
            },
            "db_id": null,
            "dead": false,
            "desc": "There's a goldfish swimming around in this little bag.",
            "drink": false,
            "equipped": null,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "locked_edge": null,
            "name": "goldfish in a bag",
            "name_prefix": "a",
            "names": [
                "goldfish in a bag"
            ],
            "node_id": "goldfish_in_a_bag_11",
            "object": true,
            "on_use": null,
            "room": false,
            "size": 5,
            "stats": {
                "damage": 0,
                "defense": 0
            },
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "hat_5": {
            "agent": false,
            "classes": [
                "object",
                "wearable"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "carrier_12__dead__"
            },
            "db_id": null,
            "dead": false,
            "desc": "The hat has 'test' written across the front.",
            "drink": false,
            "equipped": null,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "locked_edge": null,
            "name": "hat",
            "name_prefix": "a",
            "names": [
                "hat"
            ],
            "node_id": "hat_5",
            "object": true,
            "on_use": null,
            "room": false,
            "size": 1,
            "stats": {
                "defense": 1
            },
            "surface_type": "on",
            "value": 1,
            "wearable": true,
            "wieldable": false
        },
        "main_room_0": {
            "agent": false,
            "classes": [
                "room"
            ],
            "contain_size": 1999,
            "contained_nodes": {
                "carrier_12__dead__": {
                    "target_id": "carrier_12__dead__"
                },
                "chest_7": {
                    "target_id": "chest_7"
                },
                "sword_dealer_14": {
                    "target_id": "sword_dealer_14"
                },
                "table_6": {
                    "target_id": "table_6"
                }
            },
            "container_node": {
                "target_id": "VOID"
            },
            "db_id": null,
            "desc": "A main room to be used in a test. Doesn't have any other interesting properties beyond that.",
            "extra_desc": "If you look very closely, you can observe testing as it occurs.",
            "grid_location": [
                0,
                0,
                0
            ],
            "name": "Main room",
            "name_prefix": "the",
            "names": [
                "Main room"
            ],
            "neighbors": {
                "east_room_2": {
                    "examine_desc": null,
                    "label": "east",
                    "locked_edge": null,
                    "target_id": "east_room_2"
                },
                "north_room_1": {
                    "examine_desc": null,
                    "label": "north",
                    "locked_edge": null,
                    "target_id": "north_room_1"
                }
            },
            "node_id": "main_room_0",
            "object": false,
            "room": true,
            "size": 2000,
            "surface_type": "in"
        },
        "north_room_1": {
            "agent": false,
            "classes": [
                "room"
            ],
            "contain_size": 2000,
            "contained_nodes": {
                "trained_monkey_13": {
                    "target_id": "trained_monkey_13"
                }
            },
            "container_node": {
                "target_id": "VOID"
            },
            "db_id": null,
            "desc": "A north room to be used in a test. Doesn't have any other interesting properties beyond that.",
            "extra_desc": "If you look very closely, you can observe that nothing is here.",
            "grid_location": [
                0,
                0,
                0
            ],
            "name": "north room",
            "name_prefix": "the",
            "names": [
                "north room"
            ],
            "neighbors": {
                "main_room_0": {
                    "examine_desc": null,
                    "label": "south",
                    "locked_edge": null,
                    "target_id": "main_room_0"
                }
            },
            "node_id": "north_room_1",
            "object": false,
            "room": true,
            "size": 2000,
            "surface_type": "in"
        },
        "something_to_drink_20": {
            "agent": false,
            "classes": [
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "carrier_12__dead__"
            },
            "db_id": null,
            "dead": false,
            "desc": "This apple is clearly poisoned.",
            "drink": true,
            "equipped": null,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "locked_edge": null,
            "name": "something to drink",
            "name_prefix": "a",
            "names": [
                "something to drink"
            ],
            "node_id": "something_to_drink_20",
            "object": true,
            "on_use": null,
            "room": false,
            "size": 1,
            "stats": {
                "damage": 0,
                "defense": 0
            },
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "sword_dealer_14": {
            "agent": true,
            "aggression": 0,
            "attack_tagged_agents": [],
            "blocked_by": {},
            "blocking": null,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {},
            "container_node": {
                "target_id": "main_room_0"
            },
            "damage": 1,
            "db_id": null,
            "dead": false,
            "defense": 0,
            "desc": "A person who deals swords.",
            "dexterity": 1000,
            "dont_accept_gifts": false,
            "followed_by": {},
            "following": null,
            "food_energy": 1,
            "health": 2,
            "is_player": false,
            "max_distance_from_start_location": 1000000,
            "max_wearable_items": 3,
            "max_wieldable_items": 1,
            "mission": "",
            "movement_energy_cost": 0.0,
            "name": "sword dealer",
            "name_prefix": "the",
            "names": [
                "sword dealer"
            ],
            "node_id": "sword_dealer_14",
            "num_wearable_items": 0,
            "num_wieldable_items": 0,
            "object": false,
            "on_events": [],
            "pacifist": false,
            "persona": "I am a sword dealer. I deal swords.",
            "quests": [],
            "room": false,
            "size": 20,
            "speed": 5,
            "strength": 0,
            "tags": [],
            "usually_npc": false
        },
        "sword_from_a_stone_4": {
            "agent": false,
            "classes": [
                "object",
                "wieldable"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "carrier_12__dead__"
            },
            "db_id": null,
            "dead": false,
            "desc": "This sword is good for slicing tests.",
            "drink": false,
            "equipped": null,
            "food": false,
            "food_energy": 0,
            "gettable": true,
            "locked_edge": null,
            "name": "sword from a stone",
            "name_prefix": "a",
            "names": [
                "sword from a stone"
            ],
            "node_id": "sword_from_a_stone_4",
            "object": true,
            "on_use": null,
            "room": false,
            "size": 5,
            "stats": {
                "damage": 1
            },
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": true
        },
        "table_6": {
            "agent": false,
            "classes": [
                "container",
                "object"
            ],
            "contain_size": 3,
            "contained_nodes": {
                "contained_object_10": {
                    "target_id": "contained_object_10"
                }
            },
            "container": true,
            "container_node": {
                "target_id": "main_room_0"
            },
            "db_id": null,
            "dead": false,
            "desc": "The small table can't hold much more.",
            "drink": false,
            "equipped": null,
            "food": false,
            "food_energy": 0,
            "gettable": false,
            "locked_edge": null,
            "name": "table",
            "name_prefix": "a",
            "names": [
                "table"
            ],
            "node_id": "table_6",
            "object": true,
            "on_use": null,
            "room": false,
            "size": 3,
            "stats": {
                "damage": 0,
                "defense": 0
            },
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "tasty_steak_to_eat_9": {
            "agent": false,
            "classes": [
                "object"
            ],
            "contain_size": 0,
            "contained_nodes": {},
            "container": false,
            "container_node": {
                "target_id": "carrier_12__dead__"
            },
            "db_id": null,
            "dead": false,
            "desc": "This steak looks delicious.",
            "drink": false,
            "equipped": null,
            "food": true,
            "food_energy": 20,
            "gettable": true,
            "locked_edge": null,
            "name": "tasty steak to eat",
            "name_prefix": "a",
            "names": [
                "tasty steak to eat"
            ],
            "node_id": "tasty_steak_to_eat_9",
            "object": true,
            "on_use": null,
            "room": false,
            "size": 1,
            "stats": {
                "damage": 0,
                "defense": 0
            },
            "surface_type": "on",
            "value": 1,
            "wearable": false,
            "wieldable": false
        },
        "trained_monkey_13": {
            "agent": true,
            "aggression": 0,
            "attack_tagged_agents": [],
            "blocked_by": {},
            "blocking": null,
            "char_type": "person",
            "classes": [
                "agent"
            ],
            "contain_size": 20,
            "contained_nodes": {},
            "container_node": {
                "target_id": "north_room_1"
            },
            "damage": 1,
            "db_id": null,
            "dead": false,
            "defense": 0,
            "desc": "A monkey that has been trained to test.",
            "dexterity": 0,
            "dont_accept_gifts": false,
            "followed_by": {},
            "following": null,
            "food_energy": 1,
            "health": 2,
            "is_player": false,
            "max_distance_from_start_location": 1000000,
            "max_wearable_items": 3,
            "max_wieldable_items": 1,
            "mission": "",
            "movement_energy_cost": 0.0,
            "name": "trained monkey",
            "name_prefix": "the",
            "names": [
                "trained monkey"
            ],
            "node_id": "trained_monkey_13",
            "num_wearable_items": 0,
            "num_wieldable_items": 0,
            "object": false,
            "on_events": [],
            "pacifist": false,
            "persona": "I am a trained monkey. I am trained to test LIGHT.",
            "quests": [],
            "room": false,
            "size": 20,
            "speed": 5,
            "strength": 0,
            "tags": [],
            "usually_npc": false
        }
    },
    "objects": [
        "carrier_12__dead__",
        "chest_7",
        "contained_object_10",
        "goldfish_in_a_bag_11",
        "hat_5",
        "something_to_drink_20",
        "sword_from_a_stone_4",
        "table_6",
        "tasty_steak_to_eat_9"
    ],
    "rooms": [
        "east_room_2",
        "main_room_0",
        "north_room_1"
    ]
}
"""
test_graph_3_after_ingest_apple = OOGraph.from_json(
    test_graph_3_after_ingest_apple
).to_json()
test_graph_3_before_ingest_drink_dict = json.loads(test_graph_3)
del test_graph_3_before_ingest_drink_dict["nodes"]["something_to_drink_20"]
del test_graph_3_before_ingest_drink_dict["nodes"]["carrier_12"]["contained_nodes"][
    "something_to_drink_20"
]
test_graph_3_before_ingest_drink_dict["nodes"]["carrier_12"]["contain_size"] += 1
test_graph_3_before_ingest_drink_dict["objects"].remove("something_to_drink_20")
test_graph_3_after_ingest_drink = OOGraph.from_json(
    json.dumps(test_graph_3_before_ingest_drink_dict)
).to_json()


class IngestEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("sword_dealer_14", "chest"),  # Cant ingest things you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "carrier"),  # Can't ingest people
        ("carrier_12", "carrier"),  # Can't ingest people
        ("carrier_12", "bag"),  # Can't ingest things not ingestable
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "apple",
            ["poison_apple_8"],
            None,
            test_graph_3_after_ingest_apple,
            [IngestEvent, DeathEvent],
        ),
        (
            "carrier_12",
            "steak",
            ["tasty_steak_to_eat_9"],
            None,
            test_graph_3_after_ingest_steak,
            [IngestEvent, HealthEvent],
        ),
        (
            "carrier_12",
            "something",
            ["something_to_drink_20"],
            None,
            test_graph_3_after_ingest_drink,
            [IngestEvent],
        ),
    ]
    EVENT_CLASS = IngestEvent


class EatEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("sword_dealer_14", "chest"),  # Cant ingest things you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "carrier"),  # Can't ingest people
        ("carrier_12", "carrier"),  # Can't ingest people
        ("carrier_12", "bag"),  # Can't ingest things not ingestable
        ("carrier_12", "something"),  # can't eat a drinkable
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "apple",
            ["poison_apple_8"],
            None,
            test_graph_3_after_ingest_apple,
            [EatEvent, DeathEvent],
        ),
        (
            "carrier_12",
            "steak",
            ["tasty_steak_to_eat_9"],
            None,
            test_graph_3_after_ingest_steak,
            [EatEvent, HealthEvent],
        ),
    ]
    EVENT_CLASS = EatEvent


class DrinkEventTest(GraphEventTests):

    INPUT_WORLD_JSON = test_graph_3
    ERROR_CASES: List[Tuple[str, str]] = [
        ("sword_dealer_14", "chest"),  # Cant ingest things you don't have
        ("carrier_12", "123"),  # Fail because the thing doesn't exist
        ("carrier_12", ""),
        ("sword_dealer_14", "carrier"),  # Can't ingest people
        ("carrier_12", "carrier"),  # Can't ingest people
        ("carrier_12", "bag"),  # Can't ingest things not ingestable
        ("carrier_12", "apple"),  # can't drink an edible
        ("carrier_12", "steak"),  # can't drink an edible
    ]
    SUCCESS_CASES: List[
        Tuple[str, str, List[str], Optional[str], str, List[Type[GraphEvent]]]
    ] = [
        (
            "carrier_12",
            "something",
            ["something_to_drink_20"],
            None,
            test_graph_3_after_ingest_drink,
            [DrinkEvent],
        )
    ]
    EVENT_CLASS = DrinkEvent


# TODO test locking

if __name__ == "__main__":
    unittest.main()
