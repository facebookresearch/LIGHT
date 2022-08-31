#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import light.modeling.loading as load
from parlai.core.script import superscript_main as parlai_cli

"""
Extends the ParlAI CLI to make light datasets available
"""


def main():
    # TODO extend to support LIGHT deploy tasks
    load.register_all_agents()
    load.register_all_tasks()
    parlai_cli()


if __name__ == "__main__":
    main()
