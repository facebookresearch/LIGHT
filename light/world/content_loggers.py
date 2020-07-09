#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.abs

import os
import uuid
import abc
import time
import json
import collections

from light.graph.events.graph_events import ArriveEvent, SpawnEvent, DeathEvent, LeaveEvent

'''
General flow:
    - A player enters
    - Save the state of the graph, dump to a file so it can be reloaded
    - Record events happening as long as player exists (meta episode is not over)
        * Events need timestamps to order, other metadata (?room?actor?)
    - Write events to log files
    - Player exits, stop recording!

Considerations:
    - some sort of history of conversation to give context (bot history here)
    - some sort of limit to avoid afk players
    - Lots of rooms, players - want to avoid super high write times (how??)

Attributes to have:
    - meta episode id
    - graph id
    episode should have events!  Events have..
        - TIMESTAMP!
        - EVENT JSON!
        - follow up?  response to?
        - actor?  room?

'''
class InteractionLogger(abc.ABC):
    '''
        Base object for interaction loggers.  Takes a reference to the graph and
        location to write data, as well as defines some methods for interfacing
    '''
    def __init__(self, graph, data_path):
        # TODO: Consider a meta information file in directory for data store, read this from
        # that file!
        self.meta_episode = 0
        self.data_path = data_path
        self.graph = graph

    def _begin_meta_episode(self):
        '''
            Handles any preprocessing associated with beginning a meta episode such as
            clearing buffers and recording initial state
        '''
        raise NotImplementedError
    
    def _end_meta_episode(self):
        '''
            Handles any postprocessing associated with the end of a meta episode 
            such as flushing buffers by writing to data location, and updating variables
        '''
        self._log_interactions()
        raise NotImplementedError
    
    def _log_interactions(self):
        '''
            Writes out the buffers to the location specified by data location, 
            handling any data specific formatting
        '''
        raise NotImplementedError

    def observe_event(self, event):
        '''
            Examine event passed in, deciding how to save it to the logs
        '''
        raise NotImplementedError


class AgentInteractionLogger(InteractionLogger):
    '''
        This interaction logger attaches to human agents in the graph, logging all
        events the human observes.  This logger also requires serializing more rooms, 
        since agent encounters many rooms along its traversal
    '''
    def __init__(self, graph, data_path, agent, max_afk_history=5, afk_turn_tolerance=25):
        super().__init__(graph, data_path)
        self.agent = agent
        self.max_afk_history = max_afk_history
        self.afk_turn_tolerance = afk_turn_tolerance

        self.turns_wo_player_action = 0 #Player is acting by virtue of this initialized!
        self.afk_context_buffer = collections.deque(maxlen=max_afk_history)
        self.event_buffer = []
        self.state_history = []
        self._logging_intialized = False
        # Does graph even want us logging? - can change to property of world
        if graph._opt is not None:
            self.is_active = graph._opt.get('dump_dialogues', True) is True
        else:
            self.is_active = True

    def _begin_meta_episode(self):
        self._clear_buffers()
        self._add_current_graph_state()
        self.turns_wo_player_action = 0
        self._logging_intialized = True

    def _clear_buffers(self):
        '''Clear the buffers storage for this logger, dumping context'''
        self.state_history.clear()
        self.event_buffer.clear()

    def _add_current_graph_state(self):
        """Make a copy of the graph state so we can replay events on top of it
        """
        try:
            self.state_history.append(self.graph.to_json_rv(self.agent.get_room().node_id))
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
            raise

    def _is_player_afk(self):
        return self.turns_wo_player_action >= self.afk_turn_tolerance

    def _end_meta_episode(self):
        self._logging_intialized = False
        self._log_interactions()
    
    def _log_interactions(self):
        # First, check graph path, then write the graph dump
        graph_path = os.path.join(self.data_path, 'light_graph_dumps')
        if not os.path.exists(graph_path):
            os.mkdir(graph_path)

        # TODO: Fix this logic for agent writing out multiple graphs
        for state in self.state_history:
            unique_graph_name = str(uuid.uuid4())
            self._last_logged_to = unique_graph_name
            graph_file_name = f'{unique_graph_name}.json'
            file_path = os.path.join(graph_path, graph_file_name)
            with open(file_path, 'w') as dump_file:
                dump_file.write(state)

        # Now, do the same for events, dumping in the light_event_dumps/rooms
        events_path = os.path.join(self.data_path, 'light_event_dumps')
        if not os.path.exists(events_path):
            os.mkdir(events_path)
        events_room_path = os.path.join(events_path, 'agent')
        if not os.path.exists(events_room_path):
            os.mkdir(events_room_path)

        event_file_name = f'{unique_graph_name}_events.json'
        events_file_path = os.path.join(events_room_path, event_file_name)
        with open(events_file_path, 'w') as dump_file:
            for event, time in self.event_buffer:
                # TODO:  If writing multiple graphs, need to reference those here 
                dump_file.write(''.join([time, '\n']))
                dump_file.write(event)

    def observe_event(self, event):
        if not self.is_active:
            return
        event_t = type(event)
        if event_t is SpawnEvent and not self._logging_intialized:
            self._begin_meta_episode()
        elif event_t is DeathEvent: # If agent is exiting or dieing or something, end meta episode
            self._end_meta_episode()

        # Get new room state
        if event_t is ArriveEvent and event.actor is self.agent:
            # NOTE: If this is before executing event, not reliable!
            self._add_current_graph_state()

        # Store context from bots, or store current events
        if (self._is_player_afk() and not event.actor is self.agent):
            self.afk_context_buffer.append((event.to_json(), time.ctime()))
        else:
            if event.actor is self.agent:
                if self._is_player_afk():
                    self.event_buffer.extend(self.afk_context_buffer)
                    self.afk_context_buffer.clear()
                self.turns_wo_player_action = 0
            else:
                self.turns_wo_player_action += 1
            self.event_buffer.append((event.to_json(), time.ctime()))

class RoomInteractionLogger(InteractionLogger):
    '''
        This interaction logger attaches to a room level node in the graph, logging all
        events which take place with human agents in the room as long as a player is still 
        in the room
    '''
    def __init__(self, graph, data_path, room_id, max_bot_history=5, afk_turn_tolerance=10):
        super().__init__(graph, data_path)
        self.room_id = room_id
        self.max_bot_history = max_bot_history
        self.afk_turn_tolerance = afk_turn_tolerance

        self.num_players_present = 0
        self.turns_wo_players = float('inf') # Technically, we have never had players
        self.bot_context_buffer = collections.deque(maxlen=max_bot_history)
        self.conversation_buffer = []
        self.state_history = []

        # Does graph even want us logging? - can change to property of world
        if graph._opt is not None:
            self.is_active = graph._opt.get('dump_dialogues', True) is True
        else:
            self.is_active = True
        
         # Initialize player count here (bc sometimes players are force moved)
        for node_id in self.graph.all_nodes[self.room_id].contained_nodes:
            if self.graph.all_nodes[node_id].agent and self.graph.all_nodes[node_id].is_player:
                self._add_player()

    def _begin_meta_episode(self):
        self._clear_buffers()
        self._init_graph_state()
        self.turns_wo_players = 0

    def _clear_buffers(self):
        '''Clear the buffers storage for this logger, dumping context'''
        self.state_history.clear()
        self.conversation_buffer.clear()
        self.conversation_buffer.extend(self.bot_context_buffer)
        self.bot_context_buffer.clear()

    def _init_graph_state(self):
        """Make a copy of the graph state so we can replay events on top of it
        """
        try:
            self.state_history.append(self.graph.to_json_rv(self.room_id))
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
            raise

    def _is_logging(self):
        return self.num_players_present > 0

    def _is_players_afk(self):
        return self.turns_wo_players >= self.afk_turn_tolerance

    def _end_meta_episode(self):
        self._log_interactions()
        self.bot_context_buffer.clear()
    
    def _log_interactions(self):
        # First, check graph path, then write the graph dump
        graph_path = os.path.join(self.data_path, 'light_graph_dumps')
        if not os.path.exists(graph_path):
            os.mkdir(graph_path)
        print("Logging for", self.room_id, "to:", graph_path)
        for state in self.state_history:
            unique_graph_name = str(uuid.uuid4())
            self._last_logged_to = unique_graph_name
            graph_file_name = f'{unique_graph_name}.json'
            file_path = os.path.join(graph_path, graph_file_name)
            with open(file_path, 'w') as dump_file:
                dump_file.write(state)

        # Now, do the same for events, dumping in the light_event_dumps/rooms
        events_path = os.path.join(self.data_path, 'light_event_dumps')
        if not os.path.exists(events_path):
            os.mkdir(events_path)
        events_room_path = os.path.join(events_path, 'room')
        if not os.path.exists(events_room_path):
            os.mkdir(events_room_path)

        event_file_name = f'{unique_graph_name}_events.json'
        events_file_path = os.path.join(events_room_path, event_file_name)
        with open(events_file_path, 'w') as dump_file:
            for event, time in self.conversation_buffer:
                # TODO:  If writing multiple graphs, need to reference those here 
                dump_file.write(''.join([time, '\n']))
                dump_file.write(event)

    def _add_player(self):
        ''' Record that a player entered the room, updating variables as needed'''
        if not self._is_logging():
            self._begin_meta_episode()
        self.num_players_present += 1

    def _remove_player(self):
        ''' Record that a player left the room, updating variables as needed'''
        self.num_players_present -= 1
        assert(self.num_players_present >= 0)
        if not self._is_logging():
            self._end_meta_episode()

    def observe_event(self, event):
        if not self.is_active:
            return

        # Check if we need to set initial logging state, or flush because we are done
        event_t = type(event)
        if (event_t is ArriveEvent or event_t is SpawnEvent) and event.actor.is_player:
            self._add_player()

        # Store context from bots, or store current events
        if not self._is_logging() or (self._is_players_afk() and not event.actor.is_player):
            self.bot_context_buffer.append((event.to_json(), time.ctime()))
        else:
            if event.actor.is_player:
                # Players are back from AFK, dump context
                if self._is_players_afk():
                    # TODO: Need to handle something related to graph state here(?)
                    self.conversation_buffer.extend(self.bot_context_buffer)
                    self.bot_context_buffer.clear()
                self.turns_wo_players = 0
            else:
                self.turns_wo_players += 1
            self.conversation_buffer.append((event.to_json(), time.ctime()))
        
        if (event_t is LeaveEvent or event_t is DeathEvent) and event.actor.is_player:
            self._remove_player()
