#!/usr/bin/env python3
from light.graph.structured_graph import OOGraph
import os
import uuid
import abc
import time
import json

'''
TODO: Decide where to place loggers - rooms or agents or ...?

TODO: Where to put the logs?  Directory, but where?  How to organize?

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
    def __init__(self, graph, data_location):
        self.meta_episode = 0
        self.data_location = data_location
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

    def observe_event(self, event):
        '''
            Examine event passed in, deciding how to save it to the logs
        '''
        raise NotImplementedError


class RoomConversationBuffer(object):
    def __init__(
        self, graph, db_location, room_id, max_bot_history=5, max_last_human_turn=10
    ):
        self.graph = graph
        self.room_id = room_id
        self.db_location = db_location
        self.max_bot_history = max_bot_history
        self.max_last_human_turn = max_last_human_turn
        self.num_humans = 0
        self.is_active = graph._opt.get('dump_dialogues', False) is True
        self._clear_buffer()

    def _clear_buffer(self):
        '''Initialize this buffer's required storage'''
        self.conversation_buffer = []
        self.last_human_turn = -1
        self.init_state = {}
        self.currently_tracking = False

    def _init_graph_state(self):
        """On the first human turn, we need to take a copy of the graph
        state for this conversation.
        """
        try:
            self.init_state = OOGraph(self.graph, self.room_id).toJSON()
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
            raise

    def _saveable_action(self, action):
        """Formats an action to be savable in the required format by the DB and
        local storage.

        We also store the state of entering agents as they are the only things
        that can change the state of a room.
        """
        if 'name' in action and action['name'] == 'arrived':
            action = action.copy()
            actor = action['actors'][0]
            action['oograph'] = OOGraph(self.graph, actor).toJSON()
            print('added action with graph')

        # TODO actions should be objects. This will be cleaner with action
        # objects
        return action

    def observe_turn(self, action):
        """When a turn is observed, we need to add it to the conversation
        buffer.

        Special considerations are made for the first human turn, as well as
        bot turns exceeding the maximum bot turns in a row.

        If it's only bot turns, we hold up to max_bot_history of
        precursory conversation. On the first human turn, we initialize the
        graph state for this episode. On an exceeding bot turn we export
        the data to the db and start a new episode.
        """
        if not self.is_active:
            return
        # Determine if human:
        is_human = False
        if 'actors' in action:
            actor = action['actors'][0]
            is_human = self.graph.get_prop(actor, 'human')

        # Handle enters and exits
        if is_human and 'name' in action:
            if action['name'] == 'arrived':
                self.enter_human()
            elif action['name'] in ['left', 'died']:
                self.exit_human()

        # If no human responses yet
        if not self.currently_tracking:
            if not is_human:
                # only fill to the max bot history
                self.conversation_buffer.append(self._saveable_action(action))
                if len(self.conversation_buffer) > self.max_bot_history:
                    self.conversation_buffer.pop(0)
                return
            elif 'content' in action:
                # Human dialogue turn, start tracking
                self.currently_tracking = True
                self._init_graph_state()

        if is_human:
            self.last_human_turn = len(self.conversation_buffer)
        self.conversation_buffer.append(self._saveable_action(action))

        if (
            len(self.conversation_buffer) - self.last_human_turn
            > self.max_last_human_turn
        ):
            self._export_and_refresh()

    def enter_human(self):
        """increment number of humans in this room."""
        self.num_humans += 1

    def exit_human(self):
        """decrement the number of humans. If no humans left, end the episode."""
        self.num_humans -= 1
        if self.num_humans == 0 and self.last_human_turn != -1:
            self._export_and_refresh()

    def _export_and_refresh(self):
        """Save the conversation to the database and locally, then refresh the
        buffer"""
        if not is_active:
            return

        data = self._to_dump_format()
        # TODO use a long-term configurable dump path
        data_path = self.graph._opt['datapath']
        dump_path = os.path.join(data_path, '/light_graph_dumps')
        if not os.path.exists(dump_path):
            os.mkdir(dump_path)
        file_name = f'{str(uuid.uuid4())}.json'
        file_path = os.path.join(dump_path, file_name)
        with open(file_path, 'w') as dump_file:
            json.dump(data, dump_file)

        # TODO convert data to db, format, then save there
        # TODO with light_db...: save

        self._clear_buffer()

    def _to_db_format(self):
        """Take all of the data present in this buffer and return the
        savable format"""
        return {
            'actions': self.conversation_buffer[: self.last_human_turn + 1],
            'state': self.init_state,
        }
