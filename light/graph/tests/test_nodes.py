#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import unittest

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


class TestGraphNodes(unittest.TestCase):
    """Unit tests for graph node base classes"""

    def test_graph_edge(self):
        """Ensure that graph edges only take graph nodes, and return
        the expected value"""
        with self.assertRaises(AssertionError):
            x = GraphEdge(None)
        void_node = GraphVoidNode()
        x = GraphEdge(void_node)
        self.assertEqual(x.get(), void_node, "Expected graph edge to return given node")

    def test_void_node(self):
        """Ensure that a void node is created with the expected properties"""
        void_node = GraphVoidNode()
        self.assertTrue(void_node.void, "Expected void node to have void attribute set")
        self.assertEqual(
            void_node.get_contain_size(),
            GraphVoidNode.INIT_CONTAIN_SIZE,
            "Contain size not expected initial size",
        )
        self.assertEqual(
            void_node.get_container(),
            void_node,
            "Void node should be contained in self",
        )
        self.assertListEqual(
            void_node.get_contents(), [void_node], "Void node should contain itself"
        )

    def test_graph_node_create(self):
        """Ensure that the expected default properties of a graph node
        are set on initialization"""
        # Test a default initialization node
        TEST_NODE_ID = "test_id"
        TEST_NODE_NAME = "test_name"
        test_node = GraphNode(TEST_NODE_ID, TEST_NODE_NAME)
        self.assertIsNone(
            test_node.container_node, "Nodes should not be contained initially"
        )
        self.assertEqual(
            len(test_node.contained_nodes), 0, "Nodes should start with 0 contained"
        )
        self.assertEqual(test_node.contain_size, GraphNode.DEFAULT_CONTAIN_SIZE)
        self.assertEqual(test_node.size, GraphNode.DEFAULT_SIZE)
        self.assertIsNone(test_node.db_id)
        self.assertEqual(test_node.node_id, TEST_NODE_ID)
        self.assertEqual(test_node.name, TEST_NODE_NAME)
        self.assertListEqual(
            test_node.names, [TEST_NODE_NAME], "Node names should default to given name"
        )
        self.assertSetEqual(test_node.classes, set(), "Classes set should start empty")
        self.assertIn(test_node.desc, UNINTERESTING_PHRASES, "Default desc not given")
        self.assertFalse(test_node.agent)
        self.assertFalse(test_node.object)
        self.assertFalse(test_node.room)
        self.assertFalse(test_node._is_from_graph)

    def test_graph_node_create_from_props(self):
        """Ensure that the expected properties of a graph node
        are extracted from the given props"""
        TEST_CONTAIN_SIZE = 1234
        TEST_SIZE = 2345
        TEST_NODE_ID = "test_id"
        TEST_NODE_NAME = "test_name"
        TEST_NODE_NAME_2 = "test_name_2"
        TEST_NAMES = [TEST_NODE_NAME, TEST_NODE_NAME_2]
        TEST_DESC = "This is a test desc"
        TEST_CLASSES = {"test_node"}
        test_props = {
            "contain_size": TEST_CONTAIN_SIZE,
            "size": TEST_SIZE,
            "names": TEST_NAMES,
            "desc": TEST_DESC,
            "classes": TEST_CLASSES,
        }
        test_node = GraphNode(TEST_NODE_ID, TEST_NODE_NAME_2, test_props)
        self.assertIsNone(
            test_node.container_node, "Nodes should not be contained initially"
        )
        self.assertEqual(
            len(test_node.contained_nodes), 0, "Nodes should start with 0 contained"
        )
        self.assertEqual(test_node.contain_size, TEST_CONTAIN_SIZE)
        self.assertEqual(test_node.size, TEST_SIZE)
        self.assertIsNone(test_node.db_id)
        self.assertEqual(test_node.node_id, TEST_NODE_ID)
        self.assertEqual(test_node.name, TEST_NODE_NAME_2)
        self.assertListEqual(
            test_node.names, TEST_NAMES, "Node names not pulled from props"
        )
        self.assertSetEqual(
            test_node.classes, TEST_CLASSES, "Classes not pulled from props"
        )
        self.assertEqual(test_node.desc, TEST_DESC, "Desc not pulled from props")
        self.assertFalse(test_node.agent)
        self.assertFalse(test_node.object)
        self.assertFalse(test_node.room)
        self.assertFalse(test_node._is_from_graph)

    def test_graph_node_props(self):
        """Ensure props can be successfully accessed via get_prop and has_prop"""
        TEST_CONTAIN_SIZE = 1234
        TEST_SIZE = 2345
        TEST_NODE_ID = "test_id"
        TEST_NODE_NAME = "test_name"
        TEST_NODE_NAME_2 = "test_name_2"
        TEST_NAMES = [TEST_NODE_NAME, TEST_NODE_NAME_2]
        TEST_DESC = "This is a test desc"
        TEST_CLASSES = {"test_node"}
        test_props = {
            "contain_size": TEST_CONTAIN_SIZE,
            "size": TEST_SIZE,
            "names": TEST_NAMES,
            "desc": TEST_DESC,
            "classes": TEST_CLASSES,
        }
        test_node = GraphNode(TEST_NODE_ID, TEST_NODE_NAME_2, test_props)

        for test_prop_name, test_prop_val in test_props.items():
            self.assertEqual(test_node.get_prop(test_prop_name), test_prop_val)

        # getprop should return False by default
        self.assertFalse(
            test_node.get_prop("totally_fake_prop"), "Missing props should be false"
        )
        self.assertFalse(test_node.has_prop("totally_fake_prop"))
        self.assertTrue(test_node.has_prop("desc"))
        test_node.set_prop("totally_fake_prop", True)
        self.assertTrue(test_node.has_prop("totally_fake_prop"))
        self.assertTrue(test_node.get_prop("totally_fake_prop"))

    def test_graph_node_containment(self):
        """Test putting graph nodes in other nodes"""
        TEST_CONTAIN_SIZE = 1000
        TEST_SIZE = 50
        CONTAINER_NAME = "container"
        CONTAINED_NAME = "contained"
        container_node = GraphNode(
            CONTAINER_NAME, CONTAINER_NAME, {"contain_size": TEST_CONTAIN_SIZE}
        )
        with self.assertRaises(AssertionError):
            container_node.add_contained_node(None)
        with self.assertRaises(AssertionError):
            container_node.add_contained_node(container_node)

        self.assertIsNone(container_node.get_container())
        self.assertListEqual(container_node.get_contents(), [])

        TINY_CONTAINER_NAME = "tiny_container"
        TINY_CONTAIN_SIZE = 1
        tiny_container_node = GraphNode(
            TINY_CONTAINER_NAME,
            TINY_CONTAINER_NAME,
            {"contain_size": TINY_CONTAIN_SIZE},
        )
        contained_node = GraphNode(CONTAINED_NAME, CONTAINED_NAME, {"size": TEST_SIZE})

        # Fitting checks
        with self.assertRaises(AssertionError):
            tiny_container_node.would_fit("not a node")

        self.assertFalse(tiny_container_node.would_fit(contained_node))
        self.assertTrue(container_node.would_fit(contained_node))

        with self.assertRaises(AssertionError):
            tiny_container_node.add_contained_node(contained_node)

        # contents checks
        container_node.add_contained_node(contained_node)
        self.assertEqual(
            container_node.get_contain_size(),
            TEST_CONTAIN_SIZE - TEST_SIZE,
            "add_contained_node did not update contain size",
        )
        self.assertListEqual([contained_node], container_node.get_contents())

        # Shouldn't be able to add a node that is already contained
        with self.assertRaises(AssertionError):
            container_node.add_contained_node(contained_node)

        container_node.remove_contained_node(contained_node)
        self.assertEqual(
            container_node.get_contain_size(),
            TEST_CONTAIN_SIZE,
            "remove_contained_node did not update contain size",
        )
        self.assertListEqual(container_node.get_contents(), [])

        # container checks
        with self.assertRaises(AssertionError):
            container_node.set_container(container_node)
        with self.assertRaises(AssertionError):
            container_node.set_container(True)

        container_node.add_contained_node(contained_node)
        # Should not be able to have contained node as container
        with self.assertRaises(AssertionError):
            container_node.set_container(contained_node)
        container_node.remove_contained_node(contained_node)

        contained_node.set_container(container_node)
        self.assertEqual(contained_node.get_container(), container_node)
        contained_node.reset_container()
        self.assertIsNone(contained_node.get_container())

    def test_graph_node_moving(self):
        """Test moving nodes into one another by move_to and force_move_to"""
        TEST_CONTAIN_SIZE = 1000
        CONTAINER_NAME = "container"
        container_node = GraphNode(
            CONTAINER_NAME, CONTAINER_NAME, {"contain_size": TEST_CONTAIN_SIZE}
        )

        TINY_CONTAINER_NAME = "tiny_container"
        TINY_CONTAIN_SIZE = 1
        tiny_container_node = GraphNode(
            TINY_CONTAINER_NAME,
            TINY_CONTAINER_NAME,
            {"contain_size": TINY_CONTAIN_SIZE},
        )

        CONTAINED_NAME = "contained"
        TEST_SIZE = 50
        contained_node = GraphNode(CONTAINED_NAME, CONTAINED_NAME, {"size": TEST_SIZE})

        contained_node.move_to(container_node)
        self.assertEqual(contained_node.get_container(), container_node)
        self.assertListEqual(container_node.get_contents(), [contained_node])

        with self.assertRaises(AssertionError):
            contained_node.move_to(tiny_container_node)

        contained_node.force_move_to(tiny_container_node)
        self.assertEqual(contained_node.get_container(), tiny_container_node)
        self.assertListEqual(tiny_container_node.get_contents(), [contained_node])
        self.assertListEqual(
            container_node.get_contents(),
            [],
            "Node not moved out of old container in force_move_to",
        )

    def test_graph_node_classes(self):
        """Test setting and removing classes"""
        TEST_CONTAIN_SIZE = 1234
        TEST_SIZE = 2345
        TEST_NODE_ID = "test_id"
        TEST_NODE_NAME = "test_name"
        TEST_NODE_NAME_2 = "test_name_2"
        TEST_NAMES = [TEST_NODE_NAME, TEST_NODE_NAME_2]
        TEST_DESC = "This is a test desc"
        TEST_CLASS = "test_node"
        TEST_CLASSES = {TEST_CLASS}
        test_props = {
            "contain_size": TEST_CONTAIN_SIZE,
            "size": TEST_SIZE,
            "names": TEST_NAMES,
            "desc": TEST_DESC,
            "classes": TEST_CLASSES,
        }
        test_node = GraphNode(TEST_NODE_ID, TEST_NODE_NAME_2, test_props)
        self.assertSetEqual(test_node.classes, TEST_CLASSES)
        test_node.remove_class(TEST_CLASS)
        self.assertSetEqual(test_node.classes, set())
        test_node.add_class(TEST_CLASS)
        self.assertSetEqual(test_node.classes, TEST_CLASSES)


class TestNodeNetwork(unittest.TestCase):
    """Test cases for a set of linked graph nodes"""

    ROOM_1_NAME = "room1"
    ROOM_2_NAME = "room2"
    CONTAINER_1_NAME = "container1"
    CONTAINER_2_NAME = "container2"
    OBJECT_1_NAME = "object1"
    OBJECT_2_NAME = "object2"
    CHARACTER_1_NAME = "char1"
    CHARACTER_2_NAME = "char2"
    ROOM_1_2_LABEL = "room1toroom2"
    ROOM_2_1_LABEL = "room2toroom1"

    def setUp(self):
        """Construct a small world of a few graph nodes"""
        self.room_1 = GraphRoom(self.ROOM_1_NAME, self.ROOM_1_NAME)
        self.room_2 = GraphRoom(self.ROOM_2_NAME, self.ROOM_2_NAME)
        self.obj_1 = GraphObject(self.OBJECT_1_NAME, self.OBJECT_1_NAME)
        self.obj_2 = GraphObject(self.OBJECT_2_NAME, self.OBJECT_2_NAME)
        self.char_1 = GraphAgent(self.CHARACTER_1_NAME, self.CHARACTER_1_NAME)
        self.char_2 = GraphAgent(self.CHARACTER_2_NAME, self.CHARACTER_2_NAME)
        self.container_1 = GraphObject(
            self.CONTAINER_1_NAME, self.CONTAINER_1_NAME, {"container": True}
        )
        self.container_2 = GraphObject(
            self.CONTAINER_2_NAME, self.CONTAINER_2_NAME, {"container": True}
        )

        self.char_1.force_move_to(self.room_1)
        self.container_1.force_move_to(self.char_1)
        self.obj_1.force_move_to(self.container_1)
        self.obj_2.force_move_to(self.char_2)
        self.char_2.force_move_to(self.room_2)
        self.container_2.force_move_to(self.room_2)

        self.room_1.add_neighbor(self.room_2, self.ROOM_1_2_LABEL)
        self.room_2.add_neighbor(self.room_1, self.ROOM_2_1_LABEL)

    def test_correct_room_init(self):
        """Ensure GraphRoom works properly"""
        for room_node in [self.room_1, self.room_2]:
            self.assertIn("room", room_node.classes)
            self.assertTrue(room_node.room)
            self.assertFalse(room_node.agent)
            self.assertFalse(room_node.object)
            self.assertEqual(
                room_node.get_contain_size(), GraphRoom.DEFAULT_CONTAIN_SIZE
            )

    def test_correct_obj_init(self):
        """Ensure GraphObject works properly"""
        for object_node in [self.obj_1, self.obj_2]:
            self.assertIn("object", object_node.classes)
            self.assertFalse(object_node.agent)
            self.assertFalse(object_node.room)
            self.assertTrue(object_node.object)
            self.assertFalse(object_node.container)
            self.assertFalse(object_node.food)
            self.assertFalse(object_node.drink)
            self.assertFalse(object_node.wearable)
            self.assertFalse(object_node.wieldable)
            self.assertTrue(object_node.gettable)
            self.assertEqual(
                object_node.get_contain_size(), GraphObject.DEFAULT_CONTAIN_SIZE
            )
            self.assertEqual(object_node.size, GraphObject.DEFAULT_SIZE)

    def test_correct_container_init(self):
        """Ensure GraphObject with props works correctly"""
        for object_node in [self.container_1, self.container_2]:
            self.assertIn("object", object_node.classes)
            self.assertFalse(object_node.agent)
            self.assertFalse(object_node.room)
            self.assertTrue(object_node.object)
            self.assertTrue(object_node.container)
            self.assertFalse(object_node.food)
            self.assertFalse(object_node.drink)
            self.assertFalse(object_node.wearable)
            self.assertFalse(object_node.wieldable)
            self.assertTrue(object_node.gettable)
            self.assertEqual(
                object_node.get_contain_size(), GraphObject.DEFAULT_CONTAINER_SIZE
            )
            self.assertEqual(object_node.size, GraphObject.DEFAULT_CONTAINER_SIZE)

    def test_corect_character_init(self):
        """Ensure GraphAgent inits properly"""
        for agent_node in [self.char_1, self.char_2]:
            self.assertIn("agent", agent_node.classes)
            self.assertTrue(agent_node.agent)
            self.assertFalse(agent_node.room)
            self.assertFalse(agent_node.object)
            self.assertEqual(
                agent_node.get_contain_size(), GraphAgent.DEFAULT_CONTAIN_SIZE
            )
            self.assertEqual(agent_node.size, GraphAgent.DEFAULT_SIZE)
            self.assertEqual(agent_node.health, GraphAgent.DEFAULT_HEALTH)
            self.assertEqual(agent_node.persona, GraphAgent.DEFAULT_PERSONA)
            self.assertEqual(agent_node.aggression, GraphAgent.DEFAULT_AGGRESSION)
            self.assertEqual(agent_node.speed, GraphAgent.DEFAULT_SPEED)
            self.assertFalse(agent_node.is_player)

    def test_node_correct_containment_inits(self):
        """Ensure that the world connections are initialized as expected"""
        self.assertListEqual(self.room_1.get_neighbors(), [self.room_2])
        self.assertListEqual(self.room_2.get_neighbors(), [self.room_1])

        node_container_pairs = [
            (self.char_1, self.room_1),
            (self.container_1, self.char_1),
            (self.obj_1, self.container_1),
            (self.obj_2, self.char_2),
            (self.char_2, self.room_2),
            (self.container_2, self.room_2),
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

    def test_degenerate_room_containment(self):
        """Test cases for when a room is not the top level container"""
        self.char_1.reset_container()
        check_nodes = [self.char_1, self.container_1, self.obj_1]
        for node in check_nodes:
            self.assertFalse(node.get_room())
        self.char_1.force_move_to(self.obj_1)
        for node in check_nodes:
            with self.assertRaises(AssertionError):
                node.get_room()

    def test_node_views(self):
        """Test cases for viewing nodes, potentially from other nodes"""
        self.assertEqual(self.room_1.get_view(), self.ROOM_1_NAME)
        self.assertEqual(self.room_2.get_view(), self.ROOM_2_NAME)
        self.assertEqual(self.obj_1.get_view(), self.OBJECT_1_NAME)
        self.assertEqual(self.obj_2.get_view(), self.OBJECT_2_NAME)
        self.assertEqual(self.container_1.get_view(), self.CONTAINER_1_NAME)
        self.assertEqual(self.container_2.get_view(), self.CONTAINER_2_NAME)
        self.assertEqual(self.char_1.get_view(), self.CHARACTER_1_NAME)
        self.assertEqual(self.char_2.get_view(), self.CHARACTER_2_NAME)
        self.assertEqual(self.room_1.get_view_from(self.room_2), self.ROOM_2_1_LABEL)
        self.assertEqual(self.room_2.get_view_from(self.room_1), self.ROOM_1_2_LABEL)

    def test_follow_edges(self):
        """Test cases for establishing follow agents between agents"""
        self.assertListEqual(self.char_1.get_followers(), [])
        self.assertListEqual(self.char_2.get_followers(), [])
        self.assertIsNone(self.char_1.get_following())
        self.assertIsNone(self.char_2.get_following())

        with self.assertRaises(AssertionError):
            self.char_1.follow(None)
        with self.assertRaises(AssertionError):
            self.char_1.follow(self.obj_1)
        with self.assertRaises(AssertionError):
            self.char_1.follow(self.char_2)

        self.char_2.force_move_to(self.room_1)
        self.char_1.follow(self.char_2)

        self.assertListEqual(self.char_1.get_followers(), [])
        self.assertListEqual(self.char_2.get_followers(), [self.char_1])
        self.assertEqual(self.char_1.get_following(), self.char_2)
        self.assertIsNone(self.char_2.get_following())

        with self.assertRaises(AssertionError):
            self.char_1.follow(self.char_2)

        self.char_1.unfollow()

        self.assertListEqual(self.char_1.get_followers(), [])
        self.assertListEqual(self.char_2.get_followers(), [])
        self.assertIsNone(self.char_1.get_following())
        self.assertIsNone(self.char_2.get_following())

        with self.assertRaises(AssertionError):
            self.char_1.unfollow()

    def test_neighbor_edges(self):
        """Test cases for neighbor edges between rooms"""
        self.assertListEqual(self.room_1.get_neighbors(), [self.room_2])
        self.assertListEqual(self.room_2.get_neighbors(), [self.room_1])

        room_1_2_edge = self.room_1.get_edge_to(self.room_2)
        self.assertIsNotNone(room_1_2_edge)
        self.assertIsInstance(room_1_2_edge, NeighborEdge)
        self.assertEqual(room_1_2_edge.label, self.ROOM_1_2_LABEL)

        with self.assertRaises(AssertionError):
            self.room_1.get_edge_to(self.room_1)
        with self.assertRaises(AssertionError):
            self.room_1.get_edge_to(self.container_1)

        # Remove single edge
        self.room_1.remove_neighbor(self.room_2)
        with self.assertRaises(AssertionError):
            self.room_1.remove_neighbor(self.room_2)

        self.assertListEqual(self.room_1.get_neighbors(), [])
        self.assertListEqual(self.room_2.get_neighbors(), [self.room_1])

        room_1_2_edge = self.room_1.get_edge_to(self.room_2)
        self.assertIsNone(room_1_2_edge)

    def test_room_delete(self):
        """Ensure deletion of a room cascades all the correct cleanup"""
        deleted_nodes = self.room_1.delete_and_cleanup()
        self.assertEqual(len(deleted_nodes), 4)
        self.assertIn(self.room_1, deleted_nodes)
        self.assertIn(self.char_1, deleted_nodes)
        self.assertIn(self.obj_1, deleted_nodes)
        self.assertIn(self.container_1, deleted_nodes)

        # the edge to this room should be destroyed as well
        room_2_1_edge = self.room_2.get_edge_to(self.room_1)
        self.assertIsNone(room_2_1_edge)

    def test_agent_delete(self):
        """Ensure deletion of an agents cascades all the correct cleanup"""
        self.char_2.force_move_to(self.room_1)
        self.char_2.follow(self.char_1)
        self.char_1.follow(self.char_2)
        self.assertEqual(self.char_2.get_following(), self.char_1)
        self.assertListEqual(self.char_2.get_followers(), [self.char_1])
        deleted_nodes = self.char_1.delete_and_cleanup()

        self.assertEqual(len(deleted_nodes), 3)
        self.assertIn(self.char_1, deleted_nodes)
        self.assertIn(self.obj_1, deleted_nodes)
        self.assertIn(self.container_1, deleted_nodes)

        # following edges should be destroyed as well
        self.assertIsNone(self.char_2.get_following())
        self.assertListEqual(self.char_2.get_followers(), [])

    def test_object_delete(self):
        """Ensure deletion of an object cascades all the correct cleanup"""
        deleted_nodes = self.container_1.delete_and_cleanup()
        self.assertEqual(len(deleted_nodes), 2)
        self.assertIn(self.obj_1, deleted_nodes)
        self.assertIn(self.container_1, deleted_nodes)


if __name__ == "__main__":
    unittest.main()
