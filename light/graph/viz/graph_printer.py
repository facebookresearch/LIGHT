#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from queue import Queue
from collections import defaultdict

"""
Class that can print out a graph.

Currently, this uses internal graph methods, but the ones it
uses should probably be exposed somehow
"""


class GraphPrinter:
    def __init__(self):
        self.mapping_dict = {
            "east": (0, 1),
            "north": (-1, 0),
            "south": (1, 0),
            "west": (0, -1),
        }

    """
    Print out the given graph. This will first convert the
    graph to an internal format, which will be passed to ...
    This function can be subclassed.
    """

    def print(self, graph, node, agentid, visited=False):
        agent_location = graph.location(agentid)
        if visited:
            visited_rooms = graph._visited_rooms[agentid]
        else:
            visited_rooms = None

        def graph_location_item():
            return {
                "id": None,
                "edges": set(),
                "agent_location": False,
            }

        graph_locations = defaultdict(graph_location_item)
        queue = Queue()
        queue.put((node, (0, 0), None))
        while not queue.empty():
            next_node, location, previous_location = queue.get()
            if visited_rooms is not None and next_node not in visited_rooms:
                continue

            if location in graph_locations:
                continue

            graph_locations[location]["id"] = next_node
            if next_node == agent_location:
                graph_locations[location]["agent_location"] = True
            if previous_location:
                graph_locations[location]["edges"].add(previous_location)
                graph_locations[previous_location]["edges"].add(location)
            for edge_room in graph._node_to_edges[next_node]:
                _, room_name = edge_room
                direction = graph._node_to_edges[next_node][edge_room]["label"]
                location_diff = self.mapping_dict[direction]
                new_location = (
                    location[0] + location_diff[0],
                    location[1] + location_diff[1],
                )
                queue.put((room_name, new_location, location))

        return self.print_locations(graph_locations)

    """
    Override this to print in different formats.
    The default format is ascii.
    """

    def print_locations(self, graph_locations):
        for key in graph_locations:
            location_id = graph_locations[key]["id"]
            stripped_id = location_id.split("_")[0]
            if graph_locations[key]["agent_location"]:
                stripped_id = "*" + stripped_id + "*"
            graph_locations[key]["id"] = stripped_id
        min_row = min(location[0] for location in graph_locations)
        max_row = max(location[0] for location in graph_locations) + 1
        min_col = min(location[1] for location in graph_locations)
        max_col = max(location[1] for location in graph_locations) + 1

        def column_widths(column):
            return [
                len(graph_locations[(row, column)]["id"])
                for row in range(min_row, max_row)
                if (row, column) in graph_locations
            ]

        column_max_widths = {
            column: min(max(column_widths(column)), 500)
            for column in range(min_col, max_col)
        }

        def center_string(string, width):
            if len(string) > width:
                return string[:width]

            before_space = (width - len(string)) // 2
            after_space = width - len(string) - before_space
            return " " * before_space + string + " " * after_space

        answer_string_parts = []
        for row in range(min_row, max_row):
            for column in range(min_col, max_col):
                # print room label
                if (row, column) in graph_locations:
                    string = graph_locations[(row, column)]["id"]
                else:
                    string = ""

                answer_string_parts.append(
                    center_string(string, column_max_widths[column])
                )

                # print connection
                if column + 1 < max_col:
                    if (row, column) in graph_locations and (
                        row,
                        column + 1,
                    ) in graph_locations[(row, column)]["edges"]:
                        string = "--"
                    else:
                        string = ""
                    answer_string_parts.append(center_string(string, 4))

            # print newline
            answer_string_parts.append("\n")
            # print vertical connections
            if row + 1 < max_row:
                for _ in range(2):
                    for column in range(min_col, max_col):
                        # print connection
                        if (row, column) in graph_locations and (
                            row + 1,
                            column,
                        ) in graph_locations[(row, column)]["edges"]:
                            string = "|"
                        else:
                            string = ""
                        answer_string_parts.append(
                            center_string(string, column_max_widths[column])
                        )

                        # leave space for horizontal connections
                        answer_string_parts.append(center_string("", 4))
                    # print newline
                    answer_string_parts.append("\n")

        return "".join(answer_string_parts)
