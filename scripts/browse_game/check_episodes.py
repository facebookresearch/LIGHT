#!/usr/bin/env python3

# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Simple script to browse through episodes.
Allows searching by particular characters, or filtering by
duration.
"""

from scripts.filtering.reconstruct_logs import load_event_log
import argparse
import os.path
import glob
from collections import defaultdict
from light.graph.events.graph_events import SpeechEvent, GoEvent
from light.graph.events.base import ErrorEvent
from light.colors import Colors as C

from typing import List, Any, Tuple, Dict

Episode = Tuple[Any, Any]


COLORS = [
    C.CYAN,
    C.RED,
    C.GREEN,
    C.YELLOW,
    C.BLUE,
    C.PURPLE,
    C.RED,
    C.GREEN,
    C.YELLOW,
    C.BLUE,
    C.PURPLE,
    C.RED,
    C.GREEN,
    C.YELLOW,
    C.BLUE,
    C.PURPLE,
]
HUMAN_COLORS = [
    C.BOLD_CYAN,
    C.BOLD_RED,
    C.BOLD_GREEN,
    C.BOLD_YELLOW,
    C.BOLD_BLUE,
    C.BOLD_PURPLE,
    C.BOLD_RED,
    C.BOLD_GREEN,
    C.BOLD_YELLOW,
    C.BOLD_BLUE,
    C.BOLD_PURPLE,
    C.BOLD_RED,
    C.BOLD_GREEN,
    C.BOLD_YELLOW,
    C.BOLD_BLUE,
    C.BOLD_PURPLE,
]


def print_episode(episode: Episode) -> None:
    """
    Takes in an episode tuple (Actor, event list)
    and prints out all of the events, well formatted!
    """
    actor_to_color_id = {}
    actor, events = episode
    # get colors
    for e_pair in events:
        event = e_pair["event"]
        if not event.actor.agent:
            continue
        else:
            actor_id = event.actor.node_id
            if actor_id not in actor_to_color_id:
                actor_to_color_id[actor_id] = len(actor_to_color_id)

    # print events
    for e_pair in events:
        event = e_pair["event"]
        e_string = ""
        node_id = event.actor.node_id
        if node_id in actor_to_color_id:
            color_id = actor_to_color_id[node_id]
            color = COLORS[color_id % len(COLORS)]
            name = event.actor.get_view()
            if event.actor.is_player:
                color = HUMAN_COLORS[color_id % len(HUMAN_COLORS)]
                name = f"*{name}*"
            e_string += f"{color}{name}"
            if not isinstance(event, SpeechEvent):
                e_string += C.RESET
        else:
            e_string += event.actor.get_view()
        e_string += f" {event}{C.RESET}"
        print(e_string)


def get_stats(in_data: List[float]) -> Dict[str, float]:
    """
    Returns mean, median, 25 + 75% quartiles, min, and max
    """
    dat = sorted(in_data)
    mean = sum(dat) / len(dat)
    median = dat[len(dat) // 2]
    upper_quartile = dat[(len(dat) * 3) // 4]
    lower_quartile = dat[len(dat) // 4]
    min_val = dat[0]
    max_val = dat[-1]
    return {
        "min": min_val,
        "max": max_val,
        "upper": upper_quartile,
        "lower": lower_quartile,
        "median": median,
        "mean": mean,
        "string": f"{mean:.4f}:({min_val}|{lower_quartile}|{median}|{upper_quartile}|{max_val})",
    }


def is_multi_human(episode: Episode) -> bool:
    """
    Returns true if an episode contains two human players
    at any point throughout
    """
    char_id_to_human = set([])
    for pair in episode[1]:
        event = pair["event"]
        if not event.actor.agent:
            pass  # agent death in a puff of smoke
        elif event.actor.is_player:
            char_id_to_human.add(event.actor.node_id)
    return len(char_id_to_human) > 1


def took_actions(episode: Episode) -> bool:
    """
    Returns true if the actor did _anything_ at all
    """
    actor, events = episode
    if len(events) <= 2:
        return False
    for event in events[2:]:
        if actor.node_id == event["event"].actor.node_id:
            return True
    return False


def said_something(episode: Episode) -> bool:
    """
    Returns true if the actor _said_ anything at all
    """
    actor, events = episode
    if len(events) <= 2:
        return False
    for e_pair in events[2:]:
        event = e_pair["event"]
        if actor.node_id == event.actor.node_id and isinstance(event, SpeechEvent):
            return True
    return False


def count_dialogue_turns(episode: Episode, human_only: bool = True) -> int:
    """
    Return the count of dialogue turns in the whole episode
    """
    actor, events = episode
    count = 0
    if len(events) <= 2:
        return 0
    for e_pair in events[2:]:
        event = e_pair["event"]
        if isinstance(event, SpeechEvent) and (not human_only or event.actor.is_player):
            count += 1
    return count


def count_move_turns(episode: Episode) -> int:
    """
    Return the count of the number of rooms the actor has
    travelled through
    """
    actor, events = episode
    count = 0
    if len(events) <= 2:
        return 0
    for event in events[2:]:
        if actor.node_id == event["event"].actor.node_id and isinstance(
            event["event"], GoEvent
        ):
            count += 1
    return count


def count_human_action_counts(episodes: List[Episode]) -> Dict[str, Any]:
    """
    Return the counts of each event taken by a human
    agent in the list
    """
    action_counts = defaultdict(lambda: 0)
    for episode in episodes:
        actor, events = episode
        for e in events:
            if e["event"].actor.node_id == actor.node_id:
                action_counts[type(e["event"]).__name__] += 1
    return action_counts


def is_multi_party(episode: Episode) -> bool:
    """
    Returns true if an episode contains two human players
    at any point throughout
    """
    char_id_to_human = set([])
    for pair in episode[1]:
        event = pair["event"]
        if not event.actor.agent:
            pass  # agent death in a puff of smoke
        elif event.actor.is_player:
            char_id_to_human.add(event.actor.node_id)
    return len(char_id_to_human) > 2


def tried_unsafe(episode: Episode, check_any: bool = False) -> bool:
    """
    Returns true if an episode contains any unsafe turns
    from the core actor.
    Use check_any=True to see if any speech turns contained
    unsafe dialogue.
    """
    actor, events = episode
    if len(events) <= 2:
        return False
    for e_pair in events[2:]:
        event = e_pair["event"]
        if (check_any or actor.node_id == event.actor.node_id) and isinstance(
            event, SpeechEvent
        ):
            if not event.safe:
                return True
    return False


def had_error(episode: Episode) -> bool:
    """
    Returns true if an episode has any parsing or other errors
    """
    actor, events = episode
    if len(events) <= 2:
        return False
    for e_pair in events[2:]:
        event = e_pair["event"]
        if isinstance(event, ErrorEvent):
            return True
    return False


def get_errors(episodes: List[Episode]) -> List[ErrorEvent]:
    """
    Return the list of all error events in the whole episode list
    """
    error_events = []
    for episode in episodes:
        actor, events = episode
        for e in events:
            if isinstance(e["event"], ErrorEvent):
                error_events.append(e)
    return error_events


def extract_log_files(log_dir: str) -> List[str]:
    """
    Extract files that end in .log from a given directory
    and recursive subdirectories
    """
    glob_path = os.path.join(log_dir, "**/*.log")
    return [f for f in glob.glob(glob_path, recursive=True)]


def get_agent_episodes(agent_log_dir: str) -> List[Any]:
    """
    Parses the given log directory, and extracts the episodes within.
    Returns a list of Tuples, where the tuples contain the world, player,
    and the event list.
    """
    paths = extract_log_files(agent_log_dir)
    episodes = []
    for path in paths:
        id_to_world_map, events = load_event_log(path)
        agent = events[0][3].actor
        assert agent.is_player, "Agent episode was not a player!"
        parsed_events = [
            {"world": id_to_world_map[e[0]], "event": e[3]} for e in events
        ]
        episodes.append((agent, parsed_events))
    return episodes


# TODO hydrize
def main():
    parser = argparse.ArgumentParser(
        description="Args for the directory of log to examine"
    )

    # Only have one of a log or directory of logs
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--agent-log-dir",
        type=str,
        help="The top level directory of agent event logs to pull from",
    )
    group.add_argument(
        "--room-log-dir",
        type=str,
        help="The top level directory of room event logs to pull from",
    )
    parser.add_argument(
        "--use-interactive",
        action="store_true",
        help="Whether to drop into interactive after calculating",
    )

    FLAGS, _unknown = parser.parse_known_args()
    if FLAGS.agent_log_dir is not None:
        episodes = get_agent_episodes(FLAGS.agent_log_dir)
    elif FLAGS.room_log_dir is not None:
        raise NotImplementedException("No functionality for parsing room logs yet.")
        episodes = get_room_episodes(FLAGS.room_log_dir)

    multi_human = [e for e in episodes if is_multi_human(e)]
    multi_human_three = [e for e in episodes if is_multi_party(e)]
    action_episodes = [e for e in episodes if took_actions(e)]
    speech_episodes = [e for e in episodes if said_something(e)]
    actor_unsafe = [e for e in episodes if tried_unsafe(e)]
    any_unsafe = [e for e in episodes if tried_unsafe(e, check_any=True)]
    actor_errors = [e for e in episodes if had_error(e)]

    total_count = len(episodes)
    nontrivial_count = len(action_episodes)
    nontrivial_prop = nontrivial_count / total_count
    speech_count = len(speech_episodes)
    speech_prop = speech_count * 100 / nontrivial_count
    multi_human_count = len(multi_human)
    multi_human_prop = multi_human_count * 100 / nontrivial_count
    three_party_count = len(multi_human_three)
    three_party_prop = three_party_count * 100 / nontrivial_count
    actor_unsafe_count = len(actor_unsafe)
    actor_unsafe_prop = actor_unsafe_count * 100 / speech_count
    any_unsafe_count = len(any_unsafe)
    any_unsafe_prop = any_unsafe_count * 100 / speech_count
    error_count = len(actor_errors)
    error_prop = error_count * 100 / nontrivial_count
    speech_turn_details = get_stats(
        [count_dialogue_turns(e, human_only=False) for e in speech_episodes]
    )
    human_turn_details = get_stats([count_dialogue_turns(e) for e in speech_episodes])
    movement_turn_details = get_stats([count_move_turns(e) for e in action_episodes])
    overall_turn_details = get_stats([len(e[1]) for e in action_episodes])
    overall_action_breakdown = count_human_action_counts(action_episodes)

    speech_sorted_episodes = sorted(speech_episodes, key=count_dialogue_turns)
    move_sorted_episodes = sorted(action_episodes, key=count_move_turns)

    error_list = get_errors(action_episodes)

    print(
        f"{BOLD_CYAN}---- Episode Stats -----{C.RESET}\n"
        f"Total Count: {len(episodes)} \tNontrivial: {nontrivial_count} ({nontrivial_prop:2.2f}%)\n"
        f"{BOLD_CYAN}---- Remaining stats on Nontrivial ----{C.RESET}\n"
        f"Overall Interaction count stats: {overall_turn_details['string']}\n"
        f"Rooms Travelled stats: {movement_turn_details['string']}\n"
        f"Speech Count: {speech_count} ({speech_prop:2.2f}% of nontrivial)\n"
        f"{BOLD_YELLOW}---- Error Analysis ----{C.RESET}\n"
        f"Total errors: {len(error_list)}\n"
        f"Episodes with parse errors: {error_count} ({error_prop:2.2f}%)\n"
        f"{BOLD_CYAN}---- Remaining stats on Speech ----{C.RESET}\n"
        f"Overall speech turn stats: {speech_turn_details['string']}\n"
        f"Human speech turn stats: {human_turn_details['string']}\n"
        f"Multi-player: 2 or more: {multi_human_count} ({multi_human_prop:2.2f}%) \t"
        f"3 or more: {three_party_count} ({three_party_prop:2.2f}%)\n"
        f"{BOLD_YELLOW}---- Safety ----{C.RESET}\n"
        f"Unsafe by player: {actor_unsafe_count} ({actor_unsafe_prop:2.2f}%) \t"
        f"Unsafe by any: {any_unsafe_count} ({any_unsafe_prop:2.2f}%)\n"
        f"{BOLD_CYAN}----- Player action breakdown ----{C.RESET}\n"
        f"Overall action breakdown: {overall_action_breakdown}\n"
    )

    if FLAGS.use_interactive:
        print("Entering interactive. Call print_episode on any episode in `episodes`")
        import code

        code.interact(local=dict(globals(), **locals()))


if __name__ == "__main__":
    main()
