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
        since agent encounters many rooms along its traversal  These events go into 
        the conversation buffer, which is then sent to `.log` files at the specified path

        context_buffers serve an important role in this class to avoid bloating the event logs.
        context_buffers will log a fixed number of the most recent events when:

        1. The player goes afk.  This has the potential to avoid logging lots of noise in the room 
           that does not provide any signal on human player interactions.  When the player comes back 
           to the game, our loggers send some context of the most recent events to the log
    '''
    def __init__(self, graph, agent, data_path=DEFAULT_LOG_PATH, is_active=False, 
            max_context_history=5, afk_turn_tolerance=25):
        super().__init__(graph, data_path)
        self.agent = agent
        self.max_context_history = max_context_history
        self.afk_turn_tolerance = afk_turn_tolerance
        if graph._opt is None:
            self.is_active=is_active
        else:
            self.data_path = graph._opt.get("log_path", DEFAULT_LOG_PATH)    
            self.is_active = graph._opt.get("is_logging", False)


        self.turns_wo_player_action = 0 #Player is acting by virtue of this initialized!
        self.context_buffer = collections.deque(maxlen=max_context_history)
        self.event_buffer = []
        self.state_history = []
        self._logging_intialized = False

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
    
    def _dump_graphs(self):
        '''
            This method is responsible for dumping the graphs of the event logger 
            to file, recording the identifiers used for the graphs
        '''
        # First, check graph path, then write the graph dump
        graph_path = os.path.join(self.data_path, 'light_graph_dumps')
        if not os.path.exists(graph_path):
            os.mkdir(graph_path)

        states = []
        for state in self.state_history:
            unique_graph_name = str(uuid.uuid4())
            states.append(unique_graph_name)
            graph_file_name = f'{unique_graph_name}.json'
            file_path = os.path.join(graph_path, graph_file_name)
            with open(file_path, 'w') as dump_file:
                dump_file.write(state)
        return states

    def _dump_events(self, graph_states):
        '''
            This method is responsible for dumping the event logs, referencing the
            graph files recorded in graph_states.  An event log consist of events, where
            an event consist of 3 lines:
                serialized_graph_filename event_hash
                timestamp
                event_json
            Agent event logs are named: {agent_id}_{unique_identifier}.log
        '''
        # Now, do the same for events, dumping in the light_event_dumps/rooms
        events_path = os.path.join(self.data_path, 'light_event_dumps')
        if not os.path.exists(events_path):
            os.mkdir(events_path)
        events_agent_path = os.path.join(events_path, 'agent')
        if not os.path.exists(events_room_path):
            os.mkdir(events_room_path)

        unique_event_name = str(uuid.uuid4())
        agent_name = f'{self.agent.node_id}'.replace(" ", "_")
        event_file_name = f'{agent_name}_{unique_event_name}_events.log'
        events_file_path = os.path.join(events_agent_path, event_file_name)
        with open(events_file_path, 'w') as dump_file:
            for (idx, hashed, event, time) in self.event_buffer:
                dump_file.write(''.join([states[idx], " ", hashed, '\n']))
                dump_file.write(''.join([time, '\n']))
                dump_file.write(''.join([event, '\n']))
        return events_file_path

    def _log_interactions(self):

        graph_states = self._dump_graphs()
        self._last_graph = graph_states[-1]
        events_file_path = self._dump_events()
        # Used for testing
        self._last_event_log = events_file_path

    def observe_event(self, event):
        if not self.is_active:
            return
        event_t = type(event)
        if event_t is SpawnEvent and not self._logging_intialized:
            self._begin_meta_episode()

        # Get new room state
        if event_t is ArriveEvent and event.actor is self.agent:
            # NOTE: If this is before executing event, not reliable!
            self._add_current_graph_state()

        # Store context from bots, or store current events
        if (self._is_player_afk() and not event.actor is self.agent):
            self.context_buffer.append((len(self.state_history) - 1, event.__hash__(), 
                event.to_json(), time.ctime()))
        else:
            if event.actor is self.agent:
                if self._is_player_afk():
                    self.event_buffer.extend(self.context_buffer)
                    self.context_buffer.clear()
                self.turns_wo_player_action = 0
            else:
                self.turns_wo_player_action += 1
            self.event_buffer.append((len(self.state_history) - 1, event.__hash__(),
                event.to_json(), time.ctime()))
       
        if event_t is DeathEvent: # If agent is exiting or dieing or something, end meta episode
            self._end_meta_episode()


class RoomInteractionLogger(InteractionLogger):
    '''
        This interaction logger attaches to a room level node in the graph, logging all
        events which take place with human agents in the room as long as a player is still 
        in the room.  These events go into the conversation buffer, which is then sent to `.log`
        files at the specified path

        
        context_buffers serve an important role in this class to avoid bloating the event logs.
        context_buffers will log a fixed number of the most recent events when:

        1. There are no players in the room. This is a potential use case when an agent enters a 
           conversation between 2 or more models, and we want some context for training purposes

        2. All players go afk.  This has the potential to avoid logging lots of noise in the room 
           that does not provide any signal on human player interactions.  When players come back 
           to the game, our loggers send some context of the most recent events to the log
    '''
    def __init__(self, graph, room_id, data_path=DEFAULT_LOG_PATH, is_active=False, 
            max_context_history=5, afk_turn_tolerance=10):
        super().__init__(graph, data_path)
        self.room_id = room_id
        self.max_context_history = max_context_history
        self.afk_turn_tolerance = afk_turn_tolerance
        if graph._opt is None:
            self.is_active=is_active
        else:
            self.data_path = graph._opt.get("log_path", DEFAULT_LOG_PATH)    
            self.is_active = graph._opt.get("is_logging", False)

        self.num_players_present = 0
        self.turns_wo_players = float('inf') # Technically, we have never had players
        self.context_buffer = collections.deque(maxlen=max_context_history)
        self.conversation_buffer = []
        self.state_history = []

         # Initialize player count here (bc sometimes players are force moved)
        for node_id in self.graph.all_nodes[self.room_id].contained_nodes:
            if self.graph.all_nodes[node_id].agent and (self.graph.all_nodes[node_id].is_player or self.graph.all_nodes[node_id]._human):
                self._add_player()

    def _begin_meta_episode(self):
        self._clear_buffers()
        self._add_current_graph_state()
        self.turns_wo_players = 0

    def _clear_buffers(self):
        '''Clear the buffers storage for this logger, dumping context'''
        self.state_history.clear()
        self.conversation_buffer.clear()
        self.conversation_buffer.extend(self.context_buffer)
        self.context_buffer.clear()

    def _add_current_graph_state(self):
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
        self.context_buffer.clear()
    
    def _dump_graphs(self):
        '''
            This method is responsible for dumping the graphs of the event logger 
            to file, recording the identifiers used for the graphs
        '''
        # First, check graph path, then write the graph dump
        graph_path = os.path.join(self.data_path, 'light_graph_dumps')
        if not os.path.exists(graph_path):
            os.mkdir(graph_path)

        states = []
        for state in self.state_history:
            unique_graph_name = str(uuid.uuid4())
            states.append(unique_graph_name)
            graph_file_name = f'{unique_graph_name}.json'
            file_path = os.path.join(graph_path, graph_file_name)
            with open(file_path, 'w') as dump_file:
                dump_file.write(state)
        return states

    def _dump_events(self, graph_states):
        '''
            This method is responsible for dumping the event logs, referencing the
            graph files recorded in graph_states.  An event log consist of events, where
            an event consist of 3 lines:
                serialized_graph_filename event_hash
                timestamp
                event_json
            Room event logs are named: {room_id}_{unique_identifier}.log

        '''
        # Now, do the same for events, dumping in the light_event_dumps/rooms
        events_path = os.path.join(self.data_path, 'light_event_dumps')
        if not os.path.exists(events_path):
            os.mkdir(events_path)
        events_room_path = os.path.join(events_path, 'room')
        if not os.path.exists(events_room_path):
            os.mkdir(events_room_path)

        unique_event_name = str(uuid.uuid4())
        room_name = f'{self.room_id}'.replace(" ", "_")
        event_file_name = f'{room_name}_{unique_event_name}_events.log'
        events_file_path = os.path.join(events_room_path, event_file_name)
        with open(events_file_path, 'w') as dump_file:
            for (idx, hashed, event, time) in self.conversation_buffer:
                dump_file.write(''.join([states[idx], " ", hashed, '\n']))
                dump_file.write(''.join([time, '\n']))
                dump_file.write(''.join([event, '\n']))
        return events_file_path

    def _log_interactions(self):

        graph_states = self._dump_graphs()
        self._last_graph = graph_states[-1]
        events_file_path = self._dump_events()
        # Used for testing
        self._last_event_log = events_file_path

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
        if (event_t is ArriveEvent or event_t is SpawnEvent) and self.human_controlled(event):
            self._add_player()

        # Store context from bots, or store current events
        if not self._is_logging() or (self._is_players_afk() and not self.human_controlled(event)):
            self.context_buffer.append((len(self.state_history) - 1, event.__hash__()
                event.to_json(), time.ctime()))
        else:
            if self.human_controlled(event):
                # Players are back from AFK, dump context
                if self._is_players_afk():
                    # TODO: Need to handle something related to graph state here(?)
                    self.conversation_buffer.extend(self.context_buffer)
                    self.context_buffer.clear()
                self.turns_wo_players = 0
            else:
                self.turns_wo_players += 1
            self.conversation_buffer.append((len(self.state_history) - 1, event.__hash__(), 
                event.to_json(), time.ctime()))
        
        if (event_t is LeaveEvent or event_t is DeathEvent) and self.human_controlled(event):
            self._remove_player()

    def human_controlled(self, event):
        ''' Determines if an event is controlled by a human or not - need ._human for legacy (web)'''
        return event.actor.is_player or event.actor._human
 