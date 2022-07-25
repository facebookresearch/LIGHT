#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import abc
import collections
import os
import time
import uuid
from light.data_model.db.episodes import DBGroupName, EpisodeLogType

# TODO: Investigate changing the format from 3 line to csv or some other standard
from light.graph.events.graph_events import (
    ArriveEvent,
    DeathEvent,
    LeaveEvent,
    SoulSpawnEvent,
    SayEvent,
    TellEvent,
    ShoutEvent,
    WhisperEvent,
)

from typing import Optional, List, Set, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from light.data_model.db.episodes import EpisodeDB
    from light.graph.structured_graph import OOGraph
    from light.graph.elements.graph_nodes import GraphAgent


class InteractionLogger(abc.ABC):
    """
    Base object for interaction loggers.  Takes a reference to the graph and
    location to write data, as well as defines some methods for interfacing
    """

    def __init__(self, graph: "OOGraph", episode_db: Optional["EpisodeDB"]):
        self.episode_db = episode_db
        self.graph = graph
        self.players: Set[str] = set()
        self.actions: int = 0
        self._last_episode_logged: Optional[int] = None

        # All loggers should have graph state history and a buffer for events
        # State history is just the json of the graph the event executed on
        self.state_history: List[str] = []
        # Event buffer is (state_history_idx, event_hash, event_json, timestamp)
        # where state_history_idx is the index of the graph the event executed on
        self.event_buffer: List[Tuple[int, str, str, float]] = []

    def _begin_meta_episode(self) -> None:
        """
        Handles any preprocessing associated with beginning a meta episode such as
        clearing buffers and recording initial state
        """
        raise NotImplementedError

    def _end_meta_episode(self) -> None:
        """
        Handles any postprocessing associated with the end of a meta episode
        such as flushing buffers by writing to data location, and updating variables
        """
        self._log_interactions()
        raise NotImplementedError

    def observe_event(self, event) -> None:
        """
        Examine event passed in, deciding how to save it to the logs
        """
        raise NotImplementedError

    def _prep_graphs(self) -> List[Dict[str, str]]:
        """
        This method is responsible for preparing the graphs for this event logger
        """
        states = []
        for idx, state in enumerate(self.state_history):
            rand_id = str(uuid.uuid4())[:8]
            unique_graph_name = f"{time.time():.0f}-{idx}-{rand_id}"
            graph_file_name = f"{unique_graph_name}.json"
            states.append(
                {
                    "key": unique_graph_name,
                    "filename": graph_file_name,
                    "graph_json": state,
                }
            )
        return states

    def _prep_events(
        self,
        graph_states: List[Dict[str, str]],
        target_id: str,
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        This method is responsible for dumping the event logs, referencing the
        graph files recorded in graph_states.
        """
        unique_event_name = str(uuid.uuid4())[:8]
        id_name = f"{target_id}".replace(" ", "_")[:20]
        event_file_name = f"{id_name}_{time.time():.0f}_{unique_event_name}_events.json"
        events = []
        for (graph_idx, hashed, event, timestamp) in self.event_buffer:
            events.append(
                {
                    "graph_key": graph_states[graph_idx]["key"],
                    "hash": hashed,
                    "event_json": event,
                }
            )
        return (event_file_name, events)

    def _log_interactions(self, episode_type: "EpisodeLogType", target_id: str) -> None:
        if self.episode_db is None:
            return  # not actually logging
        graphs = self._prep_graphs()
        events = self._prep_events(graphs, target_id)
        self._last_episode_logged = self.episode_db.write_episode(
            graphs=graphs,
            events=events,
            log_type=episode_type,
            action_count=self.actions,
            players=self.players,
            group=DBGroupName.PRE_LAUNCH,  # TODO make configurable?
        )


class AgentInteractionLogger(InteractionLogger):
    """
    This interaction logger attaches to human agents in the graph, logging all
    events the human observes.  This logger also requires serializing more rooms,
    since agent encounters many rooms along its traversal  These events go into
    the conversation buffer, which is then stored in the provided EpisodeDB
    """

    def __init__(
        self,
        graph: "OOGraph",
        agent: "GraphAgent",
        episode_db: Optional["EpisodeDB"] = None,
        is_active: bool = False,
        afk_turn_tolerance: int = 30,
    ):
        super().__init__(graph, episode_db)
        self.agent = agent
        self.afk_turn_tolerance = afk_turn_tolerance
        if graph._opt is None:
            self.is_active = is_active
        else:
            self.is_active = graph._opt.get("is_logging", False)

        self.turns_wo_player_action = 0
        self._logging_intialized = False

    def _begin_meta_episode(self) -> None:
        self._clear_buffers()
        self._add_current_graph_state()
        self.turns_wo_player_action = 0
        self.actions = 0
        self._logging_intialized = True

    def _clear_buffers(self) -> None:
        """Clear the buffers storage for this logger, dumping context"""
        self.state_history.clear()
        self.event_buffer.clear()

    def _add_current_graph_state(self) -> None:
        """Make a copy of the graph state so we can replay events on top of it"""
        try:
            self.state_history.append(
                self.graph.to_json_rv(self.agent.get_room().node_id)
            )
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()
            raise

    def _is_player_afk(self) -> bool:
        return self.turns_wo_player_action >= self.afk_turn_tolerance

    def _end_meta_episode(self) -> None:
        self._logging_intialized = False
        self._add_current_graph_state()
        self._log_interactions(EpisodeLogType.AGENT, self.agent.node_id)

    def observe_event(self, event) -> None:
        if not self.is_active:
            return
        event_t = type(event)
        if event_t is SoulSpawnEvent and not self._logging_intialized:
            self._begin_meta_episode()
        elif self._is_player_afk():
            if event.actor is self.agent and not self._logging_intialized:
                self._begin_meta_episode()
                return  # Did not have prior graph state, can't log this event
            else:
                return  # skip events while AFK

        # Get new room state when moving
        if event_t is ArriveEvent and event.actor is self.agent:
            # NOTE: If this is before executing event, not reliable!
            self._add_current_graph_state()
        elif event_t not in [TellEvent, SayEvent, ShoutEvent, WhisperEvent]:
            self.actions += 1

        # Keep track of presence
        if event.actor is self.agent:
            self.turns_wo_player_action = 0
        else:
            self.turns_wo_player_action += 1

        if event.actor.is_player:
            user_id = event.actor.user_id
            if user_id is not None and user_id not in self.players:
                self.players.add(event.actor.user_id)

        # Append the particular event
        self.event_buffer.append(
            (
                len(self.state_history) - 1,
                event.__hash__(),
                event.to_json(),
                time.time(),
            )
        )

        if (event_t is DeathEvent and event.actor is self.agent) or (
            self._is_player_afk()
        ):  # If agent is exiting or dying or afk, end meta episode
            self._end_meta_episode()


class RoomInteractionLogger(InteractionLogger):
    """
    This interaction logger attaches to a room level node in the graph, logging all
    events which take place with human agents in the room as long as a player is
    still in the room.  These events go into the conversation buffer, which is
    then logged in the provided EpisodeDB
    """

    def __init__(
        self,
        graph: "OOGraph",
        room_id: str,
        episode_db: Optional["EpisodeDB"] = None,
        is_active: bool = False,
        afk_turn_tolerance: int = 30,
    ):
        super().__init__(graph, episode_db)
        self.room_id: str = room_id
        self.afk_turn_tolerance = afk_turn_tolerance
        if graph._opt is None:
            self.is_active = is_active
        else:
            self.is_active = graph._opt.get("is_logging", False)

        self.num_players_present = 0
        self.turns_wo_players = float("inf")  # Technically, we have never had players

        # Initialize player count here (bc sometimes players are force moved)
        for node_id in self.graph.all_nodes[self.room_id].contained_nodes:
            if self.graph.all_nodes[node_id].agent and (
                self.graph.all_nodes[node_id].is_player
            ):
                self._add_player()

    def _begin_meta_episode(self) -> None:
        self._clear_buffers()
        self._add_current_graph_state()
        self.turns_wo_players = 0
        self.actions = 0

    def _clear_buffers(self) -> None:
        """Clear the buffers storage for this logger"""
        self.state_history.clear()
        self.event_buffer.clear()

    def _add_current_graph_state(self) -> None:
        """Make a copy of the graph state so we can replay events on top of it"""
        try:
            self.state_history.append(self.graph.to_json_rv(self.room_id))
        except Exception as e:
            print(e)
            import traceback

            traceback.print_exc()
            raise

    def _is_logging(self) -> bool:
        return self.num_players_present > 0

    def _is_players_afk(self) -> bool:
        return self.turns_wo_players >= self.afk_turn_tolerance

    def _end_meta_episode(self) -> None:
        self._add_current_graph_state()
        self._log_interactions(EpisodeLogType.ROOM, self.room_id)

    def _add_player(self) -> None:
        """ Record that a player entered the room, updating variables as needed"""
        if not self.is_active:
            return
        if not self._is_logging():
            self._begin_meta_episode()
        self.num_players_present += 1

    def _remove_player(self) -> None:
        """ Record that a player left the room, updating variables as needed"""
        if not self.is_active:
            return
        self.num_players_present -= 1
        assert self.num_players_present >= 0
        if not self._is_logging():
            self._end_meta_episode()

    def observe_event(self, event) -> None:
        if not self.is_active:
            return

        # Check if we need to set initial logging state, or flush because we are done
        event_t = type(event)
        if (
            event_t is ArriveEvent or event_t is SoulSpawnEvent
        ) and self.human_controlled(event):
            if not self._is_logging():
                self._add_player()
                return  # Add and return to start logging
            self._add_player()

        if self._is_players_afk() or not self._is_logging():
            if not self.human_controlled(event):
                return  # Skip these events
            else:
                self._begin_meta_episode()
                return  # Don't have previous context, will start on the next one

        if event_t not in [TellEvent, SayEvent, ShoutEvent, WhisperEvent]:
            self.actions += 1

        # Keep track of human events
        if self.human_controlled(event):
            user_id = event.actor.user_id
            if user_id is not None and user_id not in self.players:
                self.players.add(event.actor.user_id)
            self.turns_wo_players = 0
        else:
            self.turns_wo_players += 1

        # Add to buffer
        self.event_buffer.append(
            (
                len(self.state_history) - 1,
                event.__hash__(),
                event.to_json(),
                time.time(),
            )
        )

        if (event_t in [LeaveEvent, DeathEvent]) and self.human_controlled(event):
            self._remove_player()
        if self._is_players_afk():
            self._end_meta_episode()

    def human_controlled(self, event) -> bool:
        """
        Determines if an event is controlled by a human or not
        """
        return event.actor.is_player
