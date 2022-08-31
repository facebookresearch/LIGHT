# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import parlai
import shutil
from pathlib import Path

light_repo_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
source_dir = os.path.join(light_repo_dir, "light")

parlai_repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(parlai.__file__)))
target_dir = os.path.join(parlai_repo_dir, "parlai_fb", "projects", "light")

assert os.path.isdir(source_dir), f"Source dir {source_dir} does not exist"
assert os.path.isdir(target_dir), f"Target dir {target_dir} does not exist"
print(f"Copying from {source_dir} to {target_dir}")
print(f"Removing current contents of {target_dir}")
shutil.rmtree(target_dir)
shutil.copytree(source_dir, target_dir)

print(f"Migrating import paths from light.* to parlai_fb.projects.light.*.")
python_files = [f for f in Path(target_dir).glob("**/*.py")]
for py_filename in python_files:
    with open(py_filename, "r") as py_file:
        file_contents = py_file.read()
    file_contents = file_contents.replace(
        "from light.", "from parlai_fb.projects.light."
    )
    file_contents = file_contents.replace(
        "import light.", "import parlai_fb.projects.light."
    )

    with open(py_filename, "w") as py_file:
        py_file.write(file_contents)
print("Done!")
