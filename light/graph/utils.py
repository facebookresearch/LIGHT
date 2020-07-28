#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Contains some helper functions that are useful across multiple files"""


def rm(d, val):
    """Removes a value from a dictionary if it exists, does nothing otherwise"""
    if val in d:
        del d[val]


def get_article(txt):
    """Provide an article for the given text (a/an)"""
    return "an" if txt[0] in ["a", "e", "i", "o", "u"] else "a"


def get_node_view_or_self(self_node, other_node):
    """Provide the display view for this node, or "you" if it is the self"""
    if self_node == other_node:
        return "you"
    return other_node.get_prefix_view()


def deprecated(f):
    """If the debug flag is set on the class that this wrapper is used in,
    loudly complain that this function is being called
    """

    def wrapper(*args, **kwargs):
        world = args[0]
        if world.debug:
            print("Call to deprecated function")
            import traceback

            traceback.print_stack()
        res = f(*args, **kwargs)
        return res

    return wrapper
