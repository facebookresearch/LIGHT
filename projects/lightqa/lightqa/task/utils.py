#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import random

from typing import List
from parlai_internal.projects.light.lightqa.data.utils import extract_entities

from parlai.tasks.wizard_of_wikipedia.agents import (
    TOKEN_NOCHOSEN,
)


def extract_knowledge(txt: str) -> List[str]:
    if not txt or not txt.split():
        return []
    entities = extract_entities(txt)
    return [e.lower() for e in (entities if entities else txt.split())]


def knowledge_from_dialogue_response(dialogue_response: str) -> str:
    """
    Get a knowledge response based on the dialogue response.

    We use a random entity from the dialogue response as knowledge. If there is no
    entity present, we use a random word. If there are no words present, we use
    TOKEN_NOCHOSEN.
    """
    knowledge_options = extract_knowledge(dialogue_response)
    if not knowledge_options:
        return TOKEN_NOCHOSEN
    return random.choice(knowledge_options)
