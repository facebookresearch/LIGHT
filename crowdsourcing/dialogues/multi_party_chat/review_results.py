#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from light.colors import Colors as C

db = LocalMephistoDB()


def format_data_for_printing(data):
    messages = data['data']['messages']
    main_actor = data['data']['agent_name']
    context = messages[0]['task_data']
    first_message_time = messages[0]['timestamp']
    location = context['location']
    loc_text = f"{C.BOLD_BLUE}{location['name']}{C.RESET}: {location['description']}"
    character = context['persona']
    char_text = f"{C.BOLD_GREEN}{character['name']}{C.RESET}: {character['persona']}"
    messages = messages[1:]

    def format_message(message):
        color = C.BOLD_GREEN if message['id'].lower() == character['name'].lower() else C.RESET
        return f"{color}{message['id']}{C.RESET}: {message['text']}"


    formatted_messages = [format_message(m) for m in messages]
    message_text = "\n".join(formatted_messages)

    player_messages = [m for m in messages if m['id'].lower() == character['name'].lower()]
    message_count = len(player_messages)
    avg_message_len = sum([len(m['text'].split()) for m in player_messages])/message_count
    timestamps = [0] + [m['timestamp'] - first_message_time for m in player_messages]
    durations = [timestamps[i+1]-timestamps[i] for i in range(message_count)]
    avg_duration = sum(durations)/message_count
    min_duration = min(durations)

    stats = (
        f"Messages: {message_count}  -  AVG len: {avg_message_len:.2f}\n"
        f"AVG duration: {avg_duration:.2f}   -  min duration: {min_duration:.2f}"
    )

    return f"{stats}\n{loc_text}\n{char_text}\n{message_text}"


def main():
    db = LocalMephistoDB()
    run_examine_or_review(db, format_data_for_printing)


if __name__ == '__main__':
    main()
