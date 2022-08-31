# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3
# Generates a visualization of a map in HTML.


def cell(x, y, grid, maxsz=25):
    loc = (x, y, 0)
    if loc not in grid:
        title = "EMPTY"
        return "<wbox><font color=white>" + "_" * maxsz + "</font></wbox>"
    else:
        if (
            type(grid[loc]) is dict
        ):  # This logic is added to handle legacy filler room dicts
            title = grid[loc]["setting"]
        else:
            title = grid[loc].setting
        if title == "EMPTY":
            return "<wbox><font color=white>" + "_" * maxsz + "</font></wbox>"
    if len(title) < maxsz:
        pad = "_" * round((maxsz - len(title)) / 2)
        title = pad + title
        pad = "_" * (maxsz - len(title))
        title += pad
    if len(title) > maxsz:
        title = title[0:maxsz]
    if (
        type(grid[loc]) is dict
    ):  # This logic is added to handle legacy filler room dicts
        hover = '<a href="" title="' + str(grid[loc]).replace('"', "'") + '">'
    else:
        hover = '<a href="" title="' + str(vars(grid[loc])).replace('"', "'") + '">'
    txt = "<box>" + hover + title + "</a></box>"
    return txt


def connection_south(x, y, grid):
    loc = (x, y, 0)
    if loc not in grid:
        return "white"
    if type(grid[loc]) is dict:
        if "south" in grid[loc]:
            return "blue"
        if "south*" in grid[loc]:
            return "green"
    else:
        if "south" in grid[loc].possible_connections:
            return "blue"
        if "south*" in grid[loc].possible_connections:
            return "green"
    return "white"


def connection_east(x, y, grid):
    loc = (x, y, 0)
    if loc not in grid:
        return "white"
    if type(grid[loc]) is dict:
        if "east" in grid[loc]:
            return "blue"
        if "east*" in grid[loc]:
            return "green"
    else:
        if "east" in grid[loc].possible_connections:
            return "blue"
        if "east*" in grid[loc].possible_connections:
            return "green"
    return "white"


def empty_space():
    gap = "<wbox>"
    for i in range(25):
        gap += "<font color=white>" + "|" + "</font>"
    gap += "</wbox>"
    return gap


def connected_cell(color):
    connected = "<wbox>"
    for i in range(25):
        if i == 12:
            connected += "<font color=" + color + ">" + "|" + "</font>"
        else:
            connected += "<font color=white>" + "_" + "</font>"
    connected += "</wbox>"
    return connected


def generate_html_map(fname, grid):
    # import pdb; pdb.set_trace()
    fw = open(fname, "w")
    fw.write("LIGHT map!! <br>\n\n")
    fw.write("<html>\n<head>\n<style>\n")
    fw.write('p { font-family: "Times New Roman", Times, serif; }\n')
    fw.write("a { text-decoration: none; color: black; }\n")
    fw.write("box { background-color: yellow; color: black; }\n")
    fw.write("wbox { background-color: white; color: white; }\n")
    fw.write("</style></head>\n<body>\n\n")

    for i in range(0, 7):
        fw.write("<br>\n")
        fw.write("<tt>")
        for j in range(0, 7):
            fw.write(cell(j, i, grid))
            color = connection_east(j, i, grid)
            txt = "<font color=" + color + ">--</font>"
            fw.write(txt)
        fw.write("<br>\n")
        for j in range(0, 7):
            color = connection_south(j, i, grid)
            if color != "white":
                fw.write(connected_cell(color))
            else:
                fw.write(empty_space())
            txt = "<font color=white>--</font>"
            fw.write(txt)
        fw.write("</tt>\n")
    fw.close()
