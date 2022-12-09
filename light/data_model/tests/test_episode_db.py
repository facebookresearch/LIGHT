#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import shutil, tempfile
from omegaconf import OmegaConf
import os
import json
import time

from light.graph.elements.graph_nodes import GraphAgent
from light.graph.structured_graph import OOGraph
from light.world.world import World, WorldConfig
from light.graph.events.graph_events import ArriveEvent, LeaveEvent, GoEvent, LookEvent
from light.world.content_loggers import AgentInteractionLogger, RoomInteractionLogger
from light.world.utils.json_utils import read_event_logs
from light.data_model.db.episodes import EpisodeDB, EpisodeLogType
from light.data_model.db.base import LightDBConfig

TEST_USER_ID = "USR-test"


class TestEpisodesDB(unittest.TestCase):
    """Unit tests for the EpisodeDB. Leverages Interaction Loggers to generate episodes"""

    def setUp(self):
        self.maxDiff = 10000
        self.data_dir = tempfile.mkdtemp()
        self.config = LightDBConfig(backend="test", file_root=self.data_dir)
        self.data_dir_copy = tempfile.mkdtemp()
        self.config_2 = LightDBConfig(backend="test", file_root=self.data_dir_copy)

    def tearDown(self):
        shutil.rmtree(self.data_dir)

    def setUp_single_room_graph(self, episode_db=None):
        # Set up the graph
        test_graph = OOGraph()
        agent_node = test_graph.add_agent("My test agent", {})
        room_node = test_graph.add_room("test room", {})
        agent_node.force_move_to(room_node)
        test_world = World(WorldConfig(is_logging=True, episode_db=episode_db), True)
        test_world.oo_graph = test_graph
        return (test_graph, test_world, agent_node, room_node)

    def test_initialize_episode_db(self):
        """Ensure it's possible to initialize the db"""
        db = EpisodeDB(self.config)

    def test_simple_room_logger_saves_and_loads_init_graph(self):
        """
        Test that the room logger properly saves and reloads the initial
        graph
        """
        # Set up the graph
        pre_time = time.time()
        episode_db = EpisodeDB(self.config)
        initial = self.setUp_single_room_graph(episode_db)
        test_graph, test_world, agent_node, room_node = initial
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]
        room_logger.episode_db = episode_db

        # Push a json episode out to the db
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)
        room_logger._begin_meta_episode()
        room_logger._end_meta_episode()

        # Mark the end time to test queries later
        episode_id = room_logger._last_episode_logged
        post_time = time.time()

        # Ensure an episode was created properly
        self.assertIsNotNone(episode_id)
        episode = episode_db.get_episode(episode_id)
        graph_map = episode.get_graph_map()
        self.assertEqual(len(episode.graphs), 2, "Expected an init and final graph")
        self.assertIsNotNone(episode.group)
        self.assertIsNotNone(episode.split)
        self.assertIsNotNone(episode.status)
        self.assertEqual(
            len(episode.actors), 0, f"No actors expected, found {episode.actors}"
        )
        self.assertEqual(
            len(episode.get_actors()),
            0,
            f"No actors expected, found {episode.get_actors()}",
        )
        self.assertEqual(
            episode.turn_count, 0, f"No turns excpected, found {episode.turn_count}"
        )
        self.assertEqual(
            episode.human_count, 0, f"No humans expected, found {episode.human_count}"
        )
        self.assertEqual(
            episode.action_count,
            0,
            f"No actions expected, found {episode.action_count}",
        )
        self.assertIn(
            episode.first_graph_id, graph_map, f"First graph not present in map"
        )
        self.assertIn(
            episode.final_graph_id, graph_map, f"Final graph not present in map"
        )

        # Test repr
        episode.__repr__()

        # Check graph equivalence
        before_graph = episode.get_before_graph(episode_db)
        before_graph_json = before_graph.to_json_rv(room_node.node_id)
        self.assertEqual(test_init_json, before_graph_json)

        after_graph = episode.get_after_graph(episode_db)
        after_graph_json = after_graph.to_json_rv(room_node.node_id)
        self.assertEqual(test_init_json, after_graph_json)

        # Check the parsed episode
        events = episode.get_parsed_events(episode_db)
        self.assertEqual(len(events), 0, f"Expected no events, found {events}")

        # Do some episode queries
        episodes = episode_db.get_episodes()
        self.assertEqual(len(episodes), 1, f"Expected one episode, found {episodes}")
        episodes = episode_db.get_episodes(
            min_creation_time=pre_time, max_creation_time=post_time
        )
        self.assertEqual(len(episodes), 1, f"Expected one episode, found {episodes}")
        episodes = episode_db.get_episodes(max_creation_time=pre_time)
        self.assertEqual(len(episodes), 0, f"Expected 0 episodes, found {episodes}")
        episodes = episode_db.get_episodes(min_creation_time=post_time)
        self.assertEqual(len(episodes), 0, f"Expected 0 episode, found {episodes}")
        episodes = episode_db.get_episodes(min_turns=0)
        self.assertEqual(len(episodes), 1, f"Expected one episode, found {episodes}")
        episodes = episode_db.get_episodes(min_turns=1)
        self.assertEqual(len(episodes), 0, f"Expected 0 episodes, found {episodes}")
        episodes = episode_db.get_episodes(min_humans=0)
        self.assertEqual(len(episodes), 1, f"Expected one episode, found {episodes}")
        episodes = episode_db.get_episodes(min_humans=1)
        self.assertEqual(len(episodes), 0, f"Expected 0 episodes, found {episodes}")
        episodes = episode_db.get_episodes(min_actions=0)
        self.assertEqual(len(episodes), 1, f"Expected one episode, found {episodes}")
        episodes = episode_db.get_episodes(min_actions=1)
        self.assertEqual(len(episodes), 0, f"Expected 0 episodes, found {episodes}")
        episodes = episode_db.get_episodes(log_type=EpisodeLogType.ROOM)
        self.assertEqual(len(episodes), 1, f"Expected 1 episodes, found {episodes}")
        episodes = episode_db.get_episodes(log_type=EpisodeLogType.AGENT)
        self.assertEqual(len(episodes), 0, f"Expected 0 episodes, found {episodes}")

    def test_simple_room_logger_saves_and_loads_event(self):
        """
        Test that the room logger properly saves and reloads an event
        """
        # Set up the graph
        episode_db = EpisodeDB(self.config)
        initial = self.setUp_single_room_graph(episode_db)
        test_graph, test_world, agent_node, room_node = initial
        agent_node.is_player = True
        agent_node.user_id = TEST_USER_ID
        room2_node = test_graph.add_room("test room2", {})
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]
        test_world.oo_graph = test_graph  # refresh logger

        # Check an event json was done correctly
        test_event = ArriveEvent(agent_node, text_content="")
        test_init_json = test_world.oo_graph.to_json_rv(agent_node.get_room().node_id)
        room_logger.observe_event(test_event)
        test_event2 = LookEvent(agent_node)
        room_logger.observe_event(test_event2)
        room_logger._end_meta_episode()

        ref_json = test_event2.to_json()
        episode_id = room_logger._last_episode_logged

        # Ensure an episode was created properly
        self.assertIsNotNone(episode_id)
        episode = episode_db.get_episode(episode_id)
        events = episode.get_parsed_events(episode_db)

        event_graph = events[0][0]
        event_list = events[0][1]
        loaded_event = event_list[0]

        # Assert the loaded event is the same as the executed one
        self.assertEqual(loaded_event.to_json(), ref_json)

        # Assert that episode queries with users
        self.assertEqual(episode.human_count, 1, "Expected one human")
        self.assertEqual(episode.get_actors(), [TEST_USER_ID], "Expected one actor")
        episodes = episode_db.get_episodes(min_humans=1)
        self.assertEqual(len(episodes), 1, f"Expected one episode, found {episodes}")
        episodes = episode_db.get_episodes(user_id=TEST_USER_ID)
        self.assertEqual(len(episodes), 1, f"Expected one episode, found {episodes}")
        episodes = episode_db.get_episodes(user_id="nonexist")
        self.assertEqual(len(episodes), 0, f"Expected 0 episodes, found {episodes}")

    def test_simple_agent_logger_saves_and_loads_init_graph(self):
        """
        Test that the agent logger properly saves and reloads the initial
        graph
        """
        # Set up the graph
        episode_db = EpisodeDB(self.config)
        initial = self.setUp_single_room_graph(episode_db)
        test_graph, test_world, agent_node, room_node = initial

        # Check the graph json was done correctly from agent's room
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)
        agent_logger = AgentInteractionLogger(test_world, agent_node)
        agent_logger._begin_meta_episode()
        agent_logger._end_meta_episode()

        # Mark the end time to test queries later
        episode_id = agent_logger._last_episode_logged
        post_time = time.time()

        # Ensure an episode was created properly
        self.assertIsNotNone(episode_id)
        episode = episode_db.get_episode(episode_id)
        graph_map = episode.get_graph_map()
        self.assertEqual(len(episode.graphs), 2, "Expected an init and final graph")
        self.assertIsNotNone(episode.group)
        self.assertIsNotNone(episode.split)
        self.assertIsNotNone(episode.status)
        self.assertEqual(
            len(episode.actors), 0, f"No actors expected, found {episode.actors}"
        )
        self.assertEqual(
            len(episode.get_actors()),
            0,
            f"No actors expected, found {episode.get_actors()}",
        )
        self.assertEqual(
            episode.turn_count, 0, f"No turns excpected, found {episode.turn_count}"
        )
        self.assertEqual(
            episode.human_count, 0, f"No humans expected, found {episode.human_count}"
        )
        self.assertEqual(
            episode.action_count,
            0,
            f"No actions expected, found {episode.action_count}",
        )
        self.assertIn(
            episode.first_graph_id, graph_map, f"First graph not present in map"
        )
        self.assertIn(
            episode.final_graph_id, graph_map, f"Final graph not present in map"
        )

        # Test repr
        episode.__repr__()

        # Check graph equivalence
        before_graph = episode.get_before_graph(episode_db)
        before_graph_json = before_graph.to_json_rv(room_node.node_id)
        self.assertEqual(test_init_json, before_graph_json)

        after_graph = episode.get_after_graph(episode_db)
        after_graph_json = after_graph.to_json_rv(room_node.node_id)
        self.assertEqual(test_init_json, after_graph_json)

        # Check the parsed episode
        events = episode.get_parsed_events(episode_db)
        self.assertEqual(len(events), 0, f"Expected no events, found {events}")

        # Check some episode queries
        episodes = episode_db.get_episodes(log_type=EpisodeLogType.AGENT)
        self.assertEqual(len(episodes), 1, f"Expected 1 episodes, found {episodes}")
        episodes = episode_db.get_episodes(log_type=EpisodeLogType.ROOM)
        self.assertEqual(len(episodes), 0, f"Expected 0 episodes, found {episodes}")

    def test_simple_agent_logger_saves_and_loads_event(self):
        """
        Test that the agent logger properly saves and reloads an event
        """
        # Set up the graph
        episode_db = EpisodeDB(self.config)
        initial = self.setUp_single_room_graph(episode_db)
        test_graph, test_world, agent_node, room_node = initial
        agent_node.is_player = True
        agent_node.user_id = TEST_USER_ID
        room2_node = test_graph.add_room("test room2", {})
        test_world.oo_graph = test_graph  # refresh logger
        room_logger = test_graph.room_id_to_loggers[room_node.node_id]
        room_logger.episode_db = episode_db
        room_logger.players.add(agent_node.user_id)

        # Check an event json was done correctly
        test_event = ArriveEvent(agent_node, text_content="")
        test_init_json = test_world.oo_graph.to_json_rv(agent_node.get_room().node_id)
        agent_logger = AgentInteractionLogger(test_world, agent_node)
        agent_logger._begin_meta_episode()
        agent_logger.observe_event(test_event)
        test_event2 = LookEvent(agent_node)
        agent_logger.observe_event(test_event2)
        agent_logger._end_meta_episode()
        ref_json = test_event2.to_json()

        episode_id = agent_logger._last_episode_logged

        # Ensure an episode was created properly
        self.assertIsNotNone(episode_id)
        episode = episode_db.get_episode(episode_id)
        events = episode.get_parsed_events(episode_db)
        self.assertEqual(len(events), 1, f"Expected 1 graph type, found {events}")

        event_graph = events[0][0]
        event_list = events[0][1]
        self.assertEqual(
            len(event_list), 2, f"Expected 2 logged events, found {event_list}"
        )
        loaded_event = event_list[1]

        # Assert the loaded event is the same as the executed one
        self.assertEqual(loaded_event.to_json(), ref_json)

        # Assert that episode queries with users
        self.assertEqual(episode.human_count, 1, "Expected one human")
        self.assertEqual(episode.get_actors(), [TEST_USER_ID], "Expected one actor")
        episodes = episode_db.get_episodes(min_humans=1)
        self.assertEqual(len(episodes), 1, f"Expected one episode, found {episodes}")
        episodes = episode_db.get_episodes(user_id=TEST_USER_ID)
        self.assertEqual(len(episodes), 1, f"Expected one episode, found {episodes}")
        episodes = episode_db.get_episodes(user_id="nonexist")
        self.assertEqual(len(episodes), 0, f"Expected 0 episodes, found {episodes}")

    def test_simple_room_logger_e2e(self):
        """
        Test that the room logger properly saves and reloads the graph and events
        """
        # Set up the graph
        episode_db = EpisodeDB(self.config)
        initial = self.setUp_single_room_graph(episode_db)
        test_graph, test_world, agent_node, room_node = initial
        agent_node.is_player = True
        agent_node.user_id = TEST_USER_ID
        room_node2 = test_graph.add_room("test room2", {})
        test_graph.add_paths_between(
            room_node, room_node2, "a path to the north", "a path to the south"
        )
        test_world.oo_graph = test_graph  # refresh logger

        # Check the room and event json was done correctly for room_node
        event_room_node_observed = LeaveEvent(
            agent_node, target_nodes=[room_node2]
        ).to_json()
        test_init_json = test_world.oo_graph.to_json_rv(room_node.node_id)

        GoEvent(agent_node, target_nodes=[room_node2]).execute(test_world)

        room_logger = test_graph.room_id_to_loggers[room_node.node_id]

        episode_id = room_logger._last_episode_logged
        episode = episode_db.get_episode(episode_id)
        events = episode.get_parsed_events(episode_db)
        self.assertEqual(len(events), 1, f"Expected 1 graph type, found {events}")

        event_graph = events[0][0]

        event_list = events[0][1]
        self.assertEqual(
            len(event_list), 2, f"Expected 2 logged events, found {event_list}"
        )
        loaded_event = event_list[1]

        ref_json = json.loads(event_room_node_observed)
        event_ref = json.loads(loaded_event.to_json())
        for k in ref_json:
            if k == "event_id":
                continue
            elif k == "target_nodes":
                self.assertEqual(ref_json[k][0]["names"], event_ref[k][0]["names"])
            else:
                self.assertEqual(
                    ref_json[k],
                    event_ref[k],
                    f"Event Json should match for LeaveEvent, misses on {k}",
                )

        # assert export works
        copy_db = episode_db.export(self.config_2)
        copy_episode = copy_db.get_episode(episode_id)
        copy_events = copy_episode.get_parsed_events(copy_db)
        self.assertEqual(len(copy_events), 1, f"Expected 1 graph type, found {events}")

        # assert user id is present in the temp dataset
        self.assertIn(agent_node.user_id, episode.actors)
        all_data = str(events)
        for key in episode.get_graph_map().keys():
            graph = episode.get_graph(key, episode_db)
            all_data += str(graph.to_json())
        self.assertIn(agent_node.user_id, all_data)

        # assert user data is scrubbed after scrub
        episode_db.anonymize_group(episode.group)
        episode = episode_db.get_episode(episode_id)
        events = episode.get_parsed_events(episode_db)
        self.assertNotIn(agent_node.user_id, episode.actors)
        self.assertNotIn(agent_node.user_id, str(events))
        for key in episode.get_graph_map().keys():
            graph = episode.get_graph(key, episode_db)
            self.assertNotIn(agent_node.user_id, str(graph.to_json()))

        # Assert user data is scrubbed from new table too
        episode = copy_db.get_episode(episode_id)
        events = episode.get_parsed_events(copy_db)
        self.assertNotIn(agent_node.user_id, episode.actors)
        self.assertNotIn(agent_node.user_id, str(events))
        for key in episode.get_graph_map().keys():
            graph = episode.get_graph(key, copy_db)
            self.assertNotIn(agent_node.user_id, str(graph.to_json()))
