# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import json
from datetime import datetime, timedelta

TARGET_FILES = [
    os.path.expanduser("~/Desktop/Hobbot_chats/light_chats_00-00-00_to_05-26-20.json"),
    os.path.expanduser("~/Desktop/Hobbot_chats/light_chats_05-27-20_to_06-23-20.json"),
]

chats = []
for TARGET_FILE in TARGET_FILES:
    with open(TARGET_FILE, "r") as chat_file:
        new_chats = json.load(chat_file)
        if isinstance(new_chats, dict):
            headers = new_chats["header"]
            rows = new_chats["rows"]
            for row in rows:
                chat = {}
                for idx, header in enumerate(headers):
                    chat[headers[idx]] = row[idx]
                chats.append(chat)
        else:
            chats += new_chats

# if isinstance(chats, dict):
#     headers = chats['header']
#     rows = chats['rows']
#     chats = []
#     for row in rows:
#         chat = {}
#         for idx, header in enumerate(headers):
#             chat[headers[idx]] = row[idx]
#         chats.append(chat)

chats = [
    c
    for c in chats
    if c["dialogue"] is not None and len(c["dialogue"].split("\\n")) > 1
]


def get_flagged(in_chats):
    return [c for c in in_chats if c["flagged_messages"] is not None]


def split_chats(
    in_chats, from_datetime=None, to_datetime=None, from_time_str=None, to_time_str=None
):
    if to_time_str is None:
        if to_datetime is None:
            to_time = datetime.now()
        else:
            to_time = to_datetime
    else:
        to_time = datetime.strptime(to_time_str, "%Y-%m-%d-%H-%M-%S")

    if from_time_str is None:
        if from_datetime is None:
            from_time = datetime.fromtimestamp(0)
        else:
            from_time = from_datetime
    else:
        from_time = datetime.strptime(from_time_str, "%Y-%m-%d-%H-%M-%S")

    filtered_chats = []
    for c in chats:
        c_time = datetime.strptime(c["ts"], "%Y-%m-%d-%H-%M-%S")
        if c_time < from_time:
            continue
        if c_time > to_time:
            continue
        filtered_chats.append(c)
    return filtered_chats


def choice_stats(in_chats):
    fin_go = 0
    fin_new_partner = 0
    fin_new_persona = 0
    fin_exit = 0
    missing = 0
    for chat in in_chats:
        messages = chat["dialogue"].split("\\n")
        if not messages[-1].startswith("C"):
            missing += 1
        elif "Go" in messages[-1]:
            fin_go += 1
        elif "New Partner" in messages[-1]:
            fin_new_partner += 1
        elif "New" in messages[-1]:
            fin_new_persona += 1
        else:
            fin_exit += 1
    continue_rate = 1 - (fin_exit + missing) / len(in_chats)
    print(
        f"Continue Rate: {continue_rate}, Go: {fin_go}, Partner: {fin_new_partner}, Persona: {fin_new_persona}, Exit: {fin_exit}, missing: {missing}"
    )


def chat_stats(in_chats):
    fin_stats = []
    total_utts = 0
    total_words = 0
    total_chats = len(in_chats)
    for chat in in_chats:
        messages = chat["dialogue"].split("\\n")
        if not messages[0].startswith("Human:"):
            messages = messages[1:]
        human_messages = [m[6:] for m in messages if m.startswith("Human: ")]
        utt_count = len(human_messages)
        if utt_count == 0:
            print(messages)
        words = " ".join(human_messages).split(" ")
        avg_utt_len = len(words) / utt_count
        total_utts += utt_count
        total_words += len(words)
        fin_stats.append(
            {
                "words": len(words),
                "utts": utt_count,
                "avg_len": avg_utt_len,
                "messages": messages,
            }
        )
    print(
        f"Total Chats: {total_chats}, Total utts: {total_utts}, Total Words: {total_words}, avg chat len {total_utts/total_chats}, avg utt len {total_words/total_utts}"
    )
    return fin_stats


def split_chats_by_model(chats):
    model_chats = {}
    for c in chats:
        model = c["model_name"]
        if model not in model_chats:
            model_chats[model] = []
        model_chats[model].append(c)
    return model_chats


import code

code.interact(local=locals())
