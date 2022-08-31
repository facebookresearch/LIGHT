# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
import json

from light.graph.elements.graph_nodes import (
    GraphNode,
    GraphVoidNode,
    GraphEdge,
    GraphAgent,
    GraphRoom,
    GraphObject,
    NeighborEdge,
    LockEdge,
    UNINTERESTING_PHRASES,
)

from light.graph.structured_graph import OOGraph


class TestGraphUnits(unittest.TestCase):
    """Test cases for setting up a structured graph"""

    ROOM_1_NAME = "room1"
    ROOM_2_NAME = "room2"
    OBJECT_1_NAME = "object1"
    CHARACTER_1_NAME = "char1"
    ROOM_1_2_LABEL = "room1toroom2"
    ROOM_2_1_LABEL = "room2toroom1"

    def test_initialize(self):
        """Ensure OOGraph inits as expected"""
        test_graph = OOGraph()
        self.assertDictEqual(test_graph.objects, {})
        self.assertDictEqual(test_graph.agents, {})
        self.assertDictEqual(test_graph.rooms, {})
        self.assertDictEqual(test_graph.all_nodes, {})
        self.assertDictEqual(test_graph.dead_nodes, {})
        self.assertIsInstance(test_graph.void, GraphVoidNode)
        self.assertEqual(test_graph.cnt, 0)
        self.assertListEqual(test_graph._nodes_to_delete, [])
        self.assertDictEqual(test_graph._deleted_nodes, {})

    def test_make_nodes(self):
        """Ensure it's possible to create nodes in an OOGraph"""
        test_graph = OOGraph()
        agent_node = test_graph.add_agent(self.CHARACTER_1_NAME, {})
        self.assertEqual(agent_node.get_container(), test_graph.void)
        self.assertIn(agent_node, list(test_graph.agents.values()))
        self.assertIn(agent_node, list(test_graph.all_nodes.values()))
        self.assertIsInstance(agent_node, GraphAgent)
        self.assertEqual(agent_node.name, self.CHARACTER_1_NAME)
        obj_node = test_graph.add_object(self.OBJECT_1_NAME, {})
        self.assertEqual(obj_node.get_container(), test_graph.void)
        self.assertIn(obj_node, list(test_graph.objects.values()))
        self.assertIn(obj_node, list(test_graph.all_nodes.values()))
        self.assertIsInstance(obj_node, GraphObject)
        self.assertEqual(obj_node.name, self.OBJECT_1_NAME)
        room_node = test_graph.add_room(self.ROOM_1_NAME, {})
        self.assertEqual(room_node.get_container(), test_graph.void)
        self.assertIn(room_node, list(test_graph.rooms.values()))
        self.assertIn(room_node, list(test_graph.all_nodes.values()))
        self.assertIsInstance(room_node, GraphRoom)
        self.assertEqual(room_node.name, self.ROOM_1_NAME)

        self.assertEqual(len(test_graph.void.get_contents()), 4)
        self.assertEqual(len(test_graph.all_nodes), 3)

        agent_id = agent_node.node_id
        obj_id = obj_node.node_id
        room_id = room_node.node_id
        self.assertIn(agent_id, test_graph.agents)
        self.assertIn(agent_id, test_graph.all_nodes)
        self.assertIn(obj_id, test_graph.objects)
        self.assertIn(obj_id, test_graph.all_nodes)
        self.assertIn(room_id, test_graph.rooms)
        self.assertIn(room_id, test_graph.all_nodes)

        self.assertEqual(test_graph.get_node(agent_id), agent_node)
        self.assertEqual(test_graph.get_node(obj_id), obj_node)
        self.assertEqual(test_graph.get_node(room_id), room_node)

        self.assertTrue(test_graph.node_exists(agent_id))
        self.assertTrue(test_graph.node_exists(obj_id))
        self.assertTrue(test_graph.node_exists(room_id))
        self.assertFalse(test_graph.node_exists("Fake node id!!"))

    def test_make_neighbor(self):
        """Ensure it's possible to create a double path between two rooms"""
        graph = OOGraph()
        room_1 = graph.add_room(self.ROOM_1_NAME, {})
        room_2 = graph.add_room(self.ROOM_2_NAME, {})
        graph.add_paths_between(
            room_1, room_2, self.ROOM_1_2_LABEL, self.ROOM_2_1_LABEL
        )
        edge = graph.get_edge(room_1.node_id, room_2.node_id)
        self.assertIsInstance(edge, GraphEdge)
        self.assertEqual(edge.label, self.ROOM_1_2_LABEL)
        edge = graph.get_edge(room_2.node_id, room_1.node_id)
        self.assertIsInstance(edge, GraphEdge)
        self.assertEqual(edge.label, self.ROOM_2_1_LABEL)

        # Can't create path from a room to itself
        with self.assertRaises(AssertionError):
            graph.add_paths_between(room_1, room_1)

    def test_rename_node(self):
        """Try to change a nodes name from the graph directly"""
        graph = OOGraph()
        agent_node = graph.add_agent(self.CHARACTER_1_NAME, {})
        self.assertEqual(agent_node.name, self.CHARACTER_1_NAME)
        new_name = "changed character name"
        graph.set_name(agent_node.node_id, new_name)
        self.assertEqual(agent_node.name, new_name)


class TestGraphFunctions(unittest.TestCase):
    """Test cases for operations on a constructed structured graph"""

    SHARED_SEARCH_TERM = "find"
    ROOM_1_NAME = "findroom1"
    ROOM_2_NAME = "findroom2"
    CONTAINER_1_NAME = "findcontainer1"
    CONTAINER_2_NAME = "findcontainer2"
    OBJECT_1_NAME = "findobject1"
    OBJECT_2_NAME = "findobject2"
    CHARACTER_1_NAME = "findchar1"
    CHARACTER_2_NAME = "findchar2"
    ROOM_1_2_LABEL = "room1toroom2"
    ROOM_2_1_LABEL = "room2toroom1"

    def setUp(self):
        """Construct a small world of a few graph nodes"""
        self.graph = OOGraph()

        self.room_1 = self.graph.add_room(self.ROOM_1_NAME, {})
        self.room_2 = self.graph.add_room(self.ROOM_2_NAME, {})
        self.obj_1 = self.graph.add_object(self.OBJECT_1_NAME, {})
        self.obj_2 = self.graph.add_object(self.OBJECT_2_NAME, {})
        self.char_1 = self.graph.add_agent(self.CHARACTER_1_NAME, {})
        self.char_2 = self.graph.add_agent(self.CHARACTER_2_NAME, {})
        self.container_1 = self.graph.add_object(
            self.CONTAINER_1_NAME, {"container": True}
        )
        self.container_2 = self.graph.add_object(
            self.CONTAINER_2_NAME, {"container": True}
        )

        self.char_1.force_move_to(self.room_1)
        self.container_1.force_move_to(self.char_1)
        self.obj_1.force_move_to(self.container_1)
        self.obj_2.force_move_to(self.char_2)
        self.char_2.force_move_to(self.room_2)
        self.container_2.force_move_to(self.room_2)

        self.graph.add_paths_between(
            self.room_1, self.room_2, self.ROOM_1_2_LABEL, self.ROOM_2_1_LABEL
        )

    def test_correct_graph_init(self):
        """Ensure world is created as expected"""
        self.assertEqual(
            len(self.graph.void.get_contents()),
            3,
            f"only rooms should still be in the void: found {self.graph.void.get_contents()}",
        )

        self.assertListEqual(self.room_1.get_neighbors(), [self.room_2])
        self.assertListEqual(self.room_2.get_neighbors(), [self.room_1])

        node_container_pairs = [
            (self.char_1, self.room_1),
            (self.container_1, self.char_1),
            (self.obj_1, self.container_1),
            (self.obj_2, self.char_2),
            (self.char_2, self.room_2),
            (self.container_2, self.room_2),
            (self.room_1, self.graph.void),
            (self.room_2, self.graph.void),
        ]
        for node, container in node_container_pairs:
            self.assertIn(node, container.get_contents())
            self.assertEqual(node.get_container(), container)

        room_1_nodes = [self.room_1, self.char_1, self.container_1, self.obj_1]
        room_2_nodes = [self.room_2, self.char_2, self.container_2, self.obj_2]
        for node in room_1_nodes:
            self.assertEqual(node.get_room(), self.room_1)
        for node in room_2_nodes:
            self.assertEqual(node.get_room(), self.room_2)

        self.graph.assert_valid()

    def test_deletion(self):
        """test deleting a node from the graph"""
        with self.assertRaises(AssertionError):
            self.graph.mark_node_for_deletion("fake_id")

        self.graph.mark_node_for_deletion(self.room_1.node_id)
        self.assertListEqual(self.graph._nodes_to_delete, [self.room_1.node_id])
        self.graph.delete_nodes()
        self.assertListEqual(self.graph._nodes_to_delete, [])
        self.assertEqual(len(self.graph._deleted_nodes), 4)
        self.assertIn(self.room_1, self.graph._deleted_nodes.values())
        self.assertIn(self.char_1, self.graph._deleted_nodes.values())
        self.assertIn(self.obj_1, self.graph._deleted_nodes.values())
        self.assertIn(self.container_1, self.graph._deleted_nodes.values())

        self.graph.assert_valid()

    def test_agent_death(self):
        """test deletion of an agent from the graph via death"""
        with self.assertRaises(AssertionError):
            self.graph.agent_die(self.room_1)

        self.assertDictEqual(self.graph._deleted_nodes, {})
        self.assertDictEqual(self.graph.dead_nodes, {})
        self.assertEqual(len(self.graph.objects), 4)
        self.assertEqual(len(self.graph.agents), 2)
        self.assertEqual(len(self.graph.all_nodes), 8)
        new_node = self.graph.agent_die(self.char_1)
        self.assertEqual(len(self.graph.objects), 5)
        self.assertEqual(len(self.graph.agents), 1)
        self.assertEqual(len(self.graph.all_nodes), 8)
        self.assertEqual(new_node.get_container(), self.room_1)
        self.assertEqual(self.container_1.get_container(), new_node)
        self.assertIn(new_node, self.room_1.get_contents())
        self.assertIn(self.container_1, new_node.get_contents())
        self.assertNotIn(self.char_1, self.room_1.get_contents())
        self.assertDictEqual(
            self.graph._deleted_nodes, {self.char_1.node_id: self.char_1}
        )
        self.assertIn(new_node, self.graph.get_dead_nodes())

        self.graph.assert_valid()

    def test_local_nodes(self):
        """ensure that graph traversing finds the correct local nodes"""
        local_nodes = self.graph.get_local_nodes(self.char_1.node_id)
        self.assertEqual(len(local_nodes), 4)
        self.assertIn(self.char_1, local_nodes)
        self.assertIn(self.container_1, local_nodes)
        self.assertIn(self.room_1, local_nodes)
        self.assertIn(self.room_2, local_nodes)

    def test_desc_to_nodes_path(self):
        """ensure it's possible to find the correct nodes by paths"""
        # can find paths that exist by path name
        nearby_paths_1 = self.graph.desc_to_nodes(
            self.ROOM_1_2_LABEL, self.char_1, "path"
        )
        self.assertListEqual(nearby_paths_1, [self.room_2])
        nearby_paths_2 = self.graph.desc_to_nodes(
            self.ROOM_2_1_LABEL, self.char_2, "path"
        )
        self.assertListEqual(nearby_paths_2, [self.room_1])

        # can find paths that exist by room name
        nearby_paths_3 = self.graph.desc_to_nodes(self.ROOM_2_NAME, self.char_1, "path")
        self.assertListEqual(nearby_paths_3, [self.room_2])

        # can't find paths that don't exist
        nearby_paths_4 = self.graph.desc_to_nodes(
            self.ROOM_2_1_LABEL, self.char_1, "path"
        )
        self.assertListEqual(nearby_paths_4, [])

        # can't find paths from non-rooms
        with self.assertRaises(AssertionError):
            self.graph.desc_to_nodes(self.ROOM_1_2_LABEL, self.container_1, "path")

    def test_desc_to_nodes_carrying(self):
        """ensure it's possible to find the correct nodes by carrying"""
        # can find nodes that are being carried
        carried_objs = self.graph.desc_to_nodes(
            self.CONTAINER_1_NAME, self.char_1, "carrying"
        )
        self.assertListEqual(carried_objs, [self.container_1])
        carried_objs = self.graph.desc_to_nodes(
            self.OBJECT_2_NAME, self.char_2, "carrying"
        )
        self.assertListEqual(carried_objs, [self.obj_2])

        # can't find nodes that aren't being carried
        carried_objs = self.graph.desc_to_nodes(
            self.ROOM_1_NAME, self.char_1, "carrying"
        )
        self.assertListEqual(carried_objs, [])
        carried_objs = self.graph.desc_to_nodes(
            self.CHARACTER_2_NAME, self.char_2, "carrying"
        )
        self.assertListEqual(carried_objs, [])

        # can't find nodes that are being carried by someone else
        carried_objs = self.graph.desc_to_nodes(
            self.OBJECT_2_NAME, self.char_1, "carrying"
        )
        self.assertListEqual(carried_objs, [])
        carried_objs = self.graph.desc_to_nodes(
            self.CONTAINER_1_NAME, self.char_2, "carrying"
        )
        self.assertListEqual(carried_objs, [])

        # can't find recursive carries
        carried_objs = self.graph.desc_to_nodes(
            self.OBJECT_1_NAME, self.char_1, "carrying"
        )
        self.assertListEqual(carried_objs, [])

        # can find many carries
        carried_objs = self.graph.desc_to_nodes("2", self.room_2, "carrying")
        self.assertListEqual(carried_objs, [self.char_2, self.container_2])

    def test_desc_to_nodes_sameloc(self):
        """ensure it's possible to find the correct nodes by same location"""
        # can find nodes that are in the same room as the current node
        sameloc_objs = self.graph.desc_to_nodes(
            self.CHARACTER_1_NAME, self.char_1, "sameloc"
        )
        self.assertListEqual(sameloc_objs, [])
        sameloc_objs = self.graph.desc_to_nodes(
            self.CHARACTER_2_NAME, self.char_2, "sameloc"
        )
        self.assertListEqual(sameloc_objs, [])
        sameloc_objs = self.graph.desc_to_nodes(
            self.CONTAINER_2_NAME, self.char_2, "sameloc"
        )
        self.assertListEqual(sameloc_objs, [self.container_2])

        # can't find nodes that are carried by the current node
        sameloc_objs = self.graph.desc_to_nodes(
            self.CONTAINER_1_NAME, self.char_1, "sameloc"
        )
        self.assertListEqual(sameloc_objs, [])
        sameloc_objs = self.graph.desc_to_nodes(
            self.OBJECT_2_NAME, self.char_2, "sameloc"
        )
        self.assertListEqual(sameloc_objs, [])

        # can't find other rooms
        sameloc_objs = self.graph.desc_to_nodes(
            self.ROOM_1_NAME, self.char_1, "sameloc"
        )
        self.assertListEqual(sameloc_objs, [])
        sameloc_objs = self.graph.desc_to_nodes(
            self.ROOM_1_2_LABEL, self.char_1, "sameloc"
        )
        self.assertListEqual(sameloc_objs, [])

    def test_desc_to_nodes_all_nearby(self):
        """ensure it's possible to find the correct nodes by all nearby"""
        # can find nodes in the same room
        sameloc_objs = self.graph.desc_to_nodes(
            self.CHARACTER_1_NAME, self.char_1, "all"
        )
        self.assertListEqual(sameloc_objs, [])
        sameloc_objs = self.graph.desc_to_nodes(
            self.CHARACTER_2_NAME, self.char_2, "all"
        )
        self.assertListEqual(sameloc_objs, [])
        sameloc_objs = self.graph.desc_to_nodes(
            self.CONTAINER_2_NAME, self.char_2, "all"
        )
        self.assertListEqual(sameloc_objs, [self.container_2])

        # can't find nodes in another room
        sameloc_objs = self.graph.desc_to_nodes(
            self.CONTAINER_2_NAME, self.char_1, "all"
        )
        self.assertListEqual(sameloc_objs, [])
        sameloc_objs = self.graph.desc_to_nodes(self.OBJECT_1_NAME, self.char_2, "all")
        self.assertListEqual(sameloc_objs, [])

        # can find nearby room by path name
        nearby_paths_1 = self.graph.desc_to_nodes(
            self.ROOM_1_2_LABEL, self.char_1, "all"
        )
        self.assertListEqual(nearby_paths_1, [self.room_2])
        nearby_paths_2 = self.graph.desc_to_nodes(
            self.ROOM_2_1_LABEL, self.char_2, "all"
        )
        self.assertListEqual(nearby_paths_2, [self.room_1])

        # can find paths that exist by room name
        nearby_paths_3 = self.graph.desc_to_nodes(self.ROOM_2_NAME, self.char_1, "all")
        self.assertListEqual(nearby_paths_3, [self.room_2])

        # can find carrying nodes
        carried_objs = self.graph.desc_to_nodes(
            self.CONTAINER_1_NAME, self.char_1, "all"
        )
        self.assertListEqual(carried_objs, [self.container_1])
        carried_objs = self.graph.desc_to_nodes(self.OBJECT_2_NAME, self.char_2, "all")
        self.assertListEqual(carried_objs, [self.obj_2])

        # ensure that examine room still works with here
        found = self.graph.desc_to_nodes("room", self.char_1, "all+here")
        self.assertListEqual(found, [self.room_1])

    def test_desc_to_nodes_container(self):
        """ensure it's possible to find the immediate container"""
        # can find the current container
        container_objs = self.graph.desc_to_nodes(
            self.CHARACTER_1_NAME, self.container_1, "contains"
        )
        self.assertListEqual(container_objs, [self.char_1])
        container_objs = self.graph.desc_to_nodes(
            self.CHARACTER_2_NAME, self.obj_2, "contains"
        )
        self.assertListEqual(container_objs, [self.char_2])

        # can't find the container's container
        container_objs = self.graph.desc_to_nodes(
            self.CHARACTER_1_NAME, self.obj_1, "contains"
        )
        self.assertListEqual(container_objs, [])

        # can't find contents
        container_objs = self.graph.desc_to_nodes(
            self.CONTAINER_1_NAME, self.char_1, "contains"
        )
        self.assertListEqual(container_objs, [])

    def test_desc_to_nodes_others(self):
        """ensure it's possible to find additional contained nodes"""
        # ensure you can find subcomponents of the already found stuff
        found = self.graph.desc_to_nodes(
            self.OBJECT_1_NAME, self.char_1, "carrying+others"
        )
        self.assertListEqual(found, [self.obj_1])

        # ensure that others doesn't find anything if nothing else selected
        ALL_NODES = [
            self.room_1,
            self.room_2,
            self.obj_1,
            self.obj_2,
            self.container_1,
            self.container_2,
            self.char_1,
            self.char_2,
        ]
        ALL_NAMES = [x.name for x in ALL_NODES]
        for node in ALL_NODES:
            for name in ALL_NAMES:
                found = self.graph.desc_to_nodes(name, node, "others")
                self.assertListEqual(found, [])

    def test_desc_to_nodes_all(self):
        """ensure it's possible to search through all nodes"""
        # ensure it's possible to find all nodes with the all setup
        ALL_NODES = [
            self.room_1,
            self.room_2,
            self.obj_1,
            self.obj_2,
            self.container_1,
            self.container_2,
            self.char_1,
            self.char_2,
        ]
        for node in ALL_NODES:
            found = self.graph.desc_to_nodes(node.name)
            self.assertListEqual(found, [node])

        # ensure we don't find anything with a weird search term
        found = self.graph.desc_to_nodes("fake_search_term")
        self.assertListEqual(found, [])

        # ensure we get shorter things first
        found = self.graph.desc_to_nodes(self.SHARED_SEARCH_TERM)
        self.assertEqual(len(found), 8)
        last_found = ""
        for curr_found in found:
            self.assertTrue(len(last_found) <= len(curr_found.name))
            last_found = curr_found.name

    def test_json_dump(self):
        """Ensure that json dumping makes the intended conversion"""
        as_json_1 = self.graph.to_json()
        self.assertIsNotNone(as_json_1)
        self.assertGreater(len(as_json_1), 0)
        for id in self.graph.get_all_ids():
            self.assertIn(id, as_json_1)
        from_json_1 = OOGraph.from_json(as_json_1)
        from_json_1.assert_valid()
        as_json_2 = from_json_1.to_json()

        # Ensure that the created and reloaded json and graphs are equivalent
        self.assertEqual(as_json_1, as_json_2)
        self.assertDictEqual(json.loads(as_json_1), json.loads(as_json_2))

    def test_json_from_room_view(self):
        """Ensure that json dumping from a room POV can be reconstructed into a graph
        with only the room"""
        as_json_1 = self.graph.to_json_rv(self.room_1.node_id)
        self.assertIsNotNone(as_json_1)
        self.assertGreater(len(as_json_1), 0)
        from_json_1 = OOGraph.from_json(as_json_1)
        from_json_1.assert_valid()
        as_json_2 = from_json_1.to_json()

        # Ensure that the created and reloaded json and is equivalent
        self.assertEqual(as_json_1, as_json_2)
        self.assertDictEqual(json.loads(as_json_1), json.loads(as_json_2))

        # Check things in room from OG graph exists
        self.assertTrue(from_json_1.node_exists(self.char_1.node_id))
        self.assertTrue(from_json_1.node_exists(self.obj_1.node_id))
        self.assertTrue(from_json_1.node_exists(self.container_1.node_id))

        # Check that things from OG. graph not in room are not included
        self.assertFalse(from_json_1.node_exists(self.char_2.node_id))
        self.assertFalse(from_json_1.node_exists(self.obj_2.node_id))
        self.assertFalse(from_json_1.node_exists(self.container_2.node_id))


if __name__ == "__main__":
    unittest.main()
