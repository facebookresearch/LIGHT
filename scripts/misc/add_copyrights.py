#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from light import LIGHT_DIR

COPYRIGHT_BASE = "Copyright (c) Meta Platforms, Inc."

COPYRIGHT_PYTHON = """
# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
COPYRIGHT_JS_LIKE = """
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

"""
PROBLEM = """
 */

/*
"""
MISDONE_COPYRIGHT = "Meta Platforms, Inc. and affiliates."
COPYRIGHT_CORRECTION = "Meta Platforms, Inc. and affiliates."
FILENAME_EXTENSIONS = ["py", "sh", "js", "css", "jsx", "ts", "tsx"]
LINE_CLEAR = "\x1b[2K"  # <-- ANSI sequence


def add_copyright_if_not_present(filename):
    file_ext = filename.split(".")[-1]
    if file_ext.lower() not in FILENAME_EXTENSIONS:
        return
    with open(filename, "r") as in_file:
        contents = in_file.read()

    if PROBLEM in contents:
        print(end=LINE_CLEAR)
        print(f"Duplicatee copyright in {filename}")

    if MISDONE_COPYRIGHT in contents:
        contents = contents.replace(MISDONE_COPYRIGHT, COPYRIGHT_CORRECTION)

        with open(filename, "w") as out_file:
            out_file.write(contents)
        print(end=LINE_CLEAR)
        print(f"Fixed header for {filename}")
    elif COPYRIGHT_BASE not in contents:
        if file_ext in ["py", "sh"]:
            contents = COPYRIGHT_PYTHON + contents
        else:
            contents = COPYRIGHT_JS_LIKE + contents

        with open(filename, "w") as out_file:
            out_file.write(contents)
        print(end=LINE_CLEAR)
        print(f"Added missing header to {filename}")


def main():
    curr_dir_list = [LIGHT_DIR]
    while len(curr_dir_list) > 0:
        curr_dir = curr_dir_list.pop(0)
        print(end=LINE_CLEAR)
        print(f"Considering directory {curr_dir}", end="\r")
        possible_targets = os.listdir(curr_dir)
        for target in possible_targets:
            target_path = os.path.join(curr_dir, target)
            if "node_modules" in target_path:
                continue
            if ".mypy_cache" in target_path:
                continue
            if "outputs" in target_path:
                continue
            if ".git" in target_path:
                continue
            if "/build" in target_path:
                continue
            if "/_generated" in target_path:
                continue
            if os.path.isdir(target_path):
                curr_dir_list.append(target_path)
            else:
                add_copyright_if_not_present(target_path)


if __name__ == "__main__":
    main()
