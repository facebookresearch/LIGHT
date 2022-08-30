#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Simple shared class of colors we can use for displaying terminal content in
visually appealing ways.
"""


class Colors:
    CYAN = "\u001b[36m"
    BOLD_CYAN = "\u001b[36;1m"
    RED = "\u001b[31m"
    BOLD_RED = "\u001b[31;1m"
    GREEN = "\u001b[32m"
    BOLD_GREEN = "\u001b[32;1m"
    YELLOW = "\u001b[33m"
    BOLD_YELLOW = "\u001b[33;1m"
    BLUE = "\u001b[34m"
    BOLD_BLUE = "\u001b[34;1m"
    PURPLE = "\u001b[35m"
    BOLD_PURPLE = "\u001b[35;1m"
    RESET = "\u001b[0m"
