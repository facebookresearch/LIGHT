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
REMOVE_COPYRIGHT_PYTHON = """
# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
OLD_COPYRIGHT_JS = """/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */
"""
OLD_COPYRIGHT_JS_2 = """/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
"""
BAD_START_SPACING = """
/****"""
MISPLACED_ENV = """
#!/usr/bin/env python3
"""
MISPLACED_ENV_2 = """#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc."""
CORRECT_ENV = """#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc."""
PROBLEM = """
 */

/*
"""
MISDONE_COPYRIGHT = "Meta Platforms, Inc. and its affiliates."
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
    elif REMOVE_COPYRIGHT_PYTHON in contents:
        contents = contents.replace(REMOVE_COPYRIGHT_PYTHON, "")

        with open(filename, "w") as out_file:
            out_file.write(contents)
        print(end=LINE_CLEAR)
        print(f"Fixed header for {filename}")
    elif OLD_COPYRIGHT_JS in contents:
        contents = contents.replace(OLD_COPYRIGHT_JS, "")

        with open(filename, "w") as out_file:
            out_file.write(contents)
        print(end=LINE_CLEAR)
        print(f"Fixed header for {filename}")
    elif OLD_COPYRIGHT_JS_2 in contents:
        contents = contents.replace(OLD_COPYRIGHT_JS_2, "")

        with open(filename, "w") as out_file:
            out_file.write(contents)
        print(end=LINE_CLEAR)
        print(f"Fixed header for {filename}")
    elif BAD_START_SPACING in contents:
        contents = contents.replace(BAD_START_SPACING, "/****")

        with open(filename, "w") as out_file:
            out_file.write(contents)
        print(end=LINE_CLEAR)
        print(f"Fixed header for {filename}")
    elif MISPLACED_ENV_2 in contents:
        contents = contents.replace(MISPLACED_ENV_2, CORRECT_ENV)

        with open(filename, "w") as out_file:
            out_file.write(contents)
        print(end=LINE_CLEAR)
        print(f"Fixed header for {filename}")
    elif MISPLACED_ENV in contents:
        contents = contents.replace(MISPLACED_ENV, "")
        contents = "#!/usr/bin/env python3\n" + contents
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
            if "add_copyrights.py" in target_path:
                continue  # false positives!
            if "node_modules" in target_path:
                continue
            if ".mypy_cache" in target_path:
                continue
            if "outputs" in target_path:
                continue
            if ".git" in target_path:
                continue
            if "build" == target:
                continue
            if "/_generated" in target_path:
                continue
            if os.path.isdir(target_path):
                curr_dir_list.append(target_path)
            else:
                add_copyright_if_not_present(target_path)


if __name__ == "__main__":
    main()
