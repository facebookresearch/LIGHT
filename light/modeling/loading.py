#!/usr/bin/env python3


# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


"""
Utils for loading agents and tasks, etc.
"""


def register_all_agents():
    # list all agents here
    # import light.modeling.agents.<> # noqa: F401
    pass


def register_all_tasks():
    # list all tasks here
    # import light.modeling.tasks.<> # noqa: F401
    import light.modeling.tasks.common_sense.agents
    import light.modeling.tasks.atomic.teacher  # noqa: F401
    import light.modeling.tasks.quests.goals.teacher  # noqa: F401
    import light.modeling.tasks.quests.wild_chats.teacher  # noqa: F401
