# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from light.data_model.light_database import (
    LIGHTDatabase,
    DB_STATUS_REVIEW,
    DB_STATUS_PROD,
    DB_STATUS_REJECTED,
)
from light.graph.structured_graph import OOGraph
import os
import json
import shutil

db = LIGHTDatabase("/Users/jju/ParlAI/data/light/fb_allowed.db")

with open(
    os.path.join(
        "/Users/jju/tmp_packages/tmp_packages/light_package", "character_emojis.json"
    ),
    "r",
) as jsonfile:
    all_persona_emojis = json.load(jsonfile)

# print(all_persona_emojis)

# Check characters against the persona emojis to clear personas that we've been using
SKIP_EMOJI_SCREEN = True
found_chars = {}
for char_name in all_persona_emojis:
    with db as ldb:
        db_chars = ldb.get_character(name=char_name)
        found_chars[char_name] = db_chars
        if not SKIP_EMOJI_SCREEN:
            if len(db_chars) > 1:
                for char in db_chars:
                    if ldb.get_id(char["id"])[0]["status"] == DB_STATUS_REVIEW:
                        if (
                            input(
                                f"{char['name']} {char['persona']}, (P)rod, (R)eject:"
                            ).lower()[0]
                            == "p"
                        ):
                            ldb.update_status(char["id"], DB_STATUS_PROD)
                        else:
                            ldb.update_status(char["id"], DB_STATUS_REJECTED)
            else:
                ldb.update_status(db_chars[0]["id"], DB_STATUS_PROD)

total_chars = 0
for char_name, chars in found_chars.items():
    total_chars += len(chars)

with db as ldb:
    db_chars = ldb.get_character()
    statuses = ldb.get_id()
    status_map = {c["id"]: c["status"] for c in statuses}
    approved_chars = [c for c in db_chars if status_map[c["id"]] == DB_STATUS_PROD]
print(len(found_chars), len(approved_chars), len(all_persona_emojis))

quest_dir = "/Users/jju/ParlAI/data/LIGHT/quests"
approved_dir = os.path.join(quest_dir, "approved")
all_quests = []
for quest_file in os.listdir(quest_dir):
    if quest_file.endswith(".json"):
        with open(os.path.join(quest_dir, quest_file), "r") as jsonfile:
            quest = json.load(jsonfile)
            quest["filename"] = quest_file
            all_quests.append(quest)
print(len(all_quests))

partner_quests = []
approved_partner_quests = []
for q in all_quests:
    graph = OOGraph.from_json(q["data"]["graph"])
    if len(graph.agents) != 2:
        continue
    partner_quests.append(q)
    both_approved = True
    for agent in graph.agents.values():
        agent_approved = False
        for a in approved_chars:
            if a["name"] == agent.name and a["persona"] == agent.persona:
                agent_approved = True
                break
        if not agent_approved:
            both_approved = False
    if both_approved:
        approved_partner_quests.append(q)
print(len(partner_quests), len(approved_partner_quests))

for q in approved_partner_quests:
    with open(os.path.join(approved_dir, q["filename"]), "w+") as out_quest:
        json.dump(q, out_quest)
