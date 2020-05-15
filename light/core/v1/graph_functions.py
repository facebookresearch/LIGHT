#!/usr/bin/env python3
import parlai_internal.projects.light.v1.callbacks as Callbacks
from parlai.utils.misc import Timer
from parlai_internal.projects.light.v1.graph_constraints import *
from parlai_internal.projects.light.v1.graph_utils import format_observation

from collections import Counter
from copy import deepcopy
import os
import random

GRAPH_FUNCTIONS = {}

# Useful constraint sets
def is_held_item(item_idx):
    return [
        {'type': 'is_type', 'in_args': [item_idx], 'args': [['object']]},
        {'type': 'no_prop', 'in_args': [item_idx], 'args': ['equipped']},
    ]


def is_equipped_item(item_idx):
    return [
        {'type': 'is_type', 'in_args': [item_idx], 'args': [['object']]},
        {'type': 'has_prop', 'in_args': [item_idx], 'args': ['equipped']},
    ]


# Functions
class GraphFunction(object):
    '''Initial description of function should only contain what the arguments
    are as set up by init, establishing a number to type relationship like:
    [Actor, item actor is carrying, container in same room as actor]
    '''
    def __init__(self, function_name, possible_arg_nums, arg_split_words,
                 arg_find_type, arg_constraints, func_constraints,
                 callback_triggers):
        '''Create a new graph function
        args:
        function name - name or array of aliases for the function
        possible_arg_nums - number or array of valid arg numbers for
            determining if given args are valid or for breaking text into
            a valid number of arguments before they're parsed into descs
        arg_split_words - array of words to be used to split input args
        arg_find_type - array of args for desc_to_nodes to use to find the
            argument at the given index, following the form
            {'type': <search type>, 'from': <arg idx of reference>}. If a
            list is given for each argument use the same element for each
        arg_constraints - constraints on whether or not found arguments are
            valid to be matched during the parsing step. Form is array of
            arrays of constraint types
        func_constraints - constraints on whether a function will pass with
            the given args, format is array of constraint types
        callback_triggers - callback hook names and argument idxs for making
            calls to callback functions upon completion of this function call
        '''
        self.name = function_name
        self.possible_arg_nums = possible_arg_nums
        self.arg_split_words = arg_split_words
        self.arg_find_type = arg_find_type
        self.arg_constraints = arg_constraints
        self.func_constraints = func_constraints
        self.callback_triggers = callback_triggers
        self.formats = {'failed': '{1} couldn\'t do that'}

    format_observation = format_observation

    def valid_args(self, graph, args):
        if 'ALL' in self.possible_arg_nums and len(args) >= 2:
            return True
        if len(args) not in self.possible_arg_nums:
            return False
        args = [a.lower() for a in args]
        loc = graph.location(args[0])
        # convert the arguments supplied to text form
        text_args = [
            graph.node_to_desc_raw(i, from_id=loc).lower() for i in args]
        # ensure that those are valid from the parser perspective
        valid, args, _args = self.parse_descs_to_args(graph, text_args)
        if not valid:
            return False
        # ensure that they pass the function constraints
        valid, _cons_passed, _failure = self.evaluate_constraint_set(
            graph,
            args,
            self.func_constraints,
        )
        return valid

    def handle(self, graph, args):
        if Callbacks.try_overrides(self, graph, args):
            return True
        is_constrained, _cons_passed, failure_action = \
            self.evaluate_constraint_set(graph, args, self.func_constraints)
        if not is_constrained:
            func_failure_action = self.get_failure_action(graph, args)
            # What failed?
            graph.send_action(args[0], func_failure_action)
            # Why it failed
            graph.send_action(args[0], failure_action)
            return False
        callback_args = deepcopy(args)
        is_successful = self.func(graph, args)
        if is_successful:
            Callbacks.handle_callbacks(self, graph, args)
            # TODO move callbacks call functionality elsewhere so other things
            # can call callbacks
            for trigger in self.callback_triggers:
                for arg in trigger['args']:
                    if arg >= len(callback_args):
                        break  # Don't have enough args for this callback
                    acting_agent = callback_args[arg]
                    # TODO return to callbacks
                    # callbacks = graph.get_prop(acting_agent, 'callbacks', {})
                    # if trigger['action'] in callbacks:
                    #     use_args = [callback_args[i] for i in trigger['args']]
                    #     Callbacks.handle(graph, callbacks[trigger['action']],
                    #                      use_args)
        return is_successful

    def func(self, graph, args):
        '''
        Execute action on the given graph
        Notation for documentation should be in the form of an action with <>'s
        around the incoming arguments in the order they are passed in. Optional
        arguments can be denoted by putting the clause in []'s.
        ex:
        <Actor> does thing with <object> [and other <object>]
        '''
        raise NotImplementedError

    def get_action_observation_format(self, action, descs):
        '''Given the action, return text to be filled by the parsed args
        Allowed to alter the descriptions if necessary
        Allowed to use the descriptions to determine the correct format as well
        '''
        if action['name'] in self.formats:
            return self.formats[action['name']]
        raise NotImplementedError

    def get_failure_action(self, graph, args, spec_fail='failed'):
        '''Returns an action for if the resolution of this function fails'''
        return {'caller': self.get_name(), 'name': spec_fail, 'actors': args,
                'room_id': graph.location(args[0])}

    def get_find_fail_text(self, arg_idx):
        '''Text displayed when an arg find during parse_text_to_args call
        fails to find valid targets for the function.
        Can be overridden to provide different messages for different failed
        arguments.
        '''
        return 'That isn\'t here'

    def get_improper_args_text(self, num_args):
        return 'Couldn\'t understand that. Try help for help with commands'

    def evaluate_constraint_set(self, graph, args, constraints):
        '''Check a particular set of arguments against the given constraints
        returns (True, cons_passed, None) if the constraints all pass
        returns (False, cons_passed, failure_action) if any constraint fails
        '''
        cons_passed = 0
        failure_action = None
        for constraint in constraints:
            con_args = [args[i] for i in ([0] + constraint['in_args'])]
            con_args += constraint['args']
            con_obj = CONSTRAINTS[constraint['type']]
            if con_obj.evaluate_constraint(graph, con_args):
                cons_passed += 1
            else:
                spec_fail = constraint.get('spec_fail', 'failed')
                failure_action = \
                    con_obj.get_failure_action(graph, con_args, spec_fail)
                break
        if failure_action is None:
            return True, cons_passed, None
        else:
            return False, cons_passed, failure_action

    def check_possibilites_vs_constraints(self, graph, output_args, arg_idx,
                                          possible_ids):
        '''Iterate through the given possible ids for a particular arg index
        and see if any match all the constraints for that argument

        Returns (True, valid_ID) on success
        Returns (False, violator_action) on failure
        '''
        constraints = self.arg_constraints[arg_idx]
        most_constraints = -1
        final_failure_action = None
        for pos_id in possible_ids:
            output_args[arg_idx] = pos_id
            success, cons_passed, failure_action = \
                self.evaluate_constraint_set(graph, output_args, constraints)
            if success:
                return True, pos_id
            else:
                output_args[arg_idx] = None
                if cons_passed > most_constraints:
                    most_constraints = cons_passed
                    final_failure_action = failure_action
        return False, final_failure_action

    def parse_text_to_args(self, graph, actor_id, text):
        '''Breaks text into function arguments based on this function's
        delimiters
        Returns:
        (None, display text, None) if parsing failed to find valid candidates
        (True, arg_ids, canonical_text_args) if parsing and constraints succeed
        (False, Failure action, matched_args)
                if parsing succeeds but constraints fail
        '''
        actor_id = actor_id.lower()
        c_arg = []
        descs = [actor_id]
        for word in text:
            if word.lower() in self.arg_split_words:
                descs.append(' '.join(c_arg))
                c_arg = []
            else:
                c_arg.append(word)
        if len(c_arg) != 0:
            descs.append(' '.join(c_arg))
        if len(descs) not in self.possible_arg_nums and \
                'ALL' not in self.possible_arg_nums:
            return (None, self.get_improper_args_text(len(descs)), None)
        return self.parse_descs_to_args(graph, descs)

    def try_callback_override_args(self, graph, args):
        output_args = [None] * (len(args))
        output_args[0] = args[0]
        args = [arg.lower() for arg in args]
        # While there are still arguments to fill
        while None in output_args:
            for arg_idx, arg_id in enumerate(output_args):
                if arg_id is not None:  # This was processed in an earlier pass
                    continue
                nearbyid = output_args[0]

                # Get the possible IDs from the graph in the area
                arg_text = args[arg_idx]
                possible_ids = graph.desc_to_nodes(arg_text, nearbyid,
                                                   'all+here')
                # can't have reflexive actions with the same arg
                for had_id in output_args:
                    if had_id in possible_ids:
                        possible_ids.remove(had_id)
                if len(possible_ids) == 0:
                    return None, None, None

                output_args[arg_idx] = possible_ids[0]

        # Determine canonical arguments
        if Callbacks.has_valid_override(self, graph, output_args):
            loc = graph.location(output_args[0])
            text_args = \
                [graph.node_to_desc_raw(i, from_id=loc) for i in output_args]
            return True, output_args, text_args
        return None, None, None

    def parse_descs_to_args_helper(self, graph, args, output_args,
                                   arg_find_idx=None):
        args = [a.lower() for a in args]
        for arg_idx, arg_id in enumerate(output_args):
            if arg_id is not None:  # This was processed in an earlier pass
                continue
            arg_find_type = self.arg_find_type[arg_idx]
            if arg_find_idx is not None:
                arg_find_type = arg_find_type[arg_find_idx]
            nearby_idx = arg_find_type['from']
            # we cant process a from when the nearby hasn't been found
            if output_args[nearby_idx] is None:
                continue
            nearbyid = output_args[nearby_idx]

            # Make sure we have all the constraints filled
            constraints = self.arg_constraints[arg_idx]
            have_all_args = True
            for constraint in constraints:
                for alt_id_idx in constraint['in_args']:
                    if arg_idx == alt_id_idx:
                        continue  # We plan to fill this slot with a guess
                    if output_args[alt_id_idx] is None:
                        # We don't have all the constraints for this
                        have_all_args = False
            if not have_all_args:
                continue

            # Get the possible IDs from the graph in the area
            arg_text = args[arg_idx]
            possible_ids = graph.desc_to_nodes(arg_text, nearbyid,
                                               arg_find_type['type'])
            # can't have reflexive actions with the same arg
            for had_id in output_args:
                if had_id in possible_ids:
                    possible_ids.remove(had_id)
            res = None
            while len(possible_ids) > 0:
                # See if any match the constraints
                success, res = self.check_possibilites_vs_constraints(
                    graph, output_args, arg_idx, possible_ids)
                if success:
                    output_args[arg_idx] = res
                    possible_ids.remove(res)
                    success_again, res, _args = \
                        self.parse_descs_to_args_helper(graph, args,
                                                        output_args,
                                                        arg_find_idx)
                    if success_again:
                        return True, None, output_args  # success!
                elif res is not None:
                    return False, res, args  # failure case, no matching option
                else:
                    break
            if res is not None:
                return False, res, args  # failure case, no matching option
            return None, self.get_find_fail_text(arg_idx), None  # failed find
        return True, '', output_args  # base case, all filled

    def parse_descs_to_args(self, graph, args):
        '''iterates through the args and the constraints, solving dependency
        order on the fly.
        '''
        # TODO improve performance by instead constructing a dependency graph
        # at runtime to avoid repeat passes through the loop and to prevent
        # circular dependencies
        args = [a.lower() for a in args]
        success, output_args, text_args = \
            self.try_callback_override_args(graph, args)
        if success:
            return success, output_args, text_args
        output_args = [None] * (len(args))
        output_args[0] = args[0]
        if 'ALL' in self.possible_arg_nums:
            output_args[1] = ' '.join(args[1:])
            return True, output_args, output_args
        args = [arg.lower() for arg in args]

        # While there are still arguments to fill
        if type(self.arg_find_type[0]) is list:
            arg_find_idx = 0
            success = False
            while arg_find_idx < len(self.arg_find_type[0]) and not success:
                output_args = [None] * (len(args))
                output_args[0] = args[0]
                success, res, output_args = \
                    self.parse_descs_to_args_helper(graph, args,
                                                    output_args, arg_find_idx)
                arg_find_idx += 1
        else:
            success, res, output_args = \
                self.parse_descs_to_args_helper(graph, args, output_args)

        if success:
            # Determine canonical arguments
            loc = graph.location(output_args[0])
            text_args = \
                [graph.node_to_desc_raw(i, from_id=loc) for i in output_args]
            return True, output_args, text_args
        else:
            return success, res, output_args

    def get_name(self):
        '''Get the canonical name of this function'''
        name = self.name
        if type(name) is list:
            name = name[0]
        return name

    def get_canonical_form(self, graph, args):
        '''Get canonical form for the given args on this function'''
        if 'ALL' in self.possible_arg_nums:
            # All is reserved for functions that take all arguments
            return ' '.join(args)
        loc = graph.location(args[0])
        text_args = \
            [graph.node_to_desc_raw(i, from_id=loc) for i in args]
        if len(args) == 1:
            return self.get_name()
        if len(self.arg_split_words) == 0 or len(args) == 2:
            return self.get_name() + ' ' + text_args[1]
        return (self.get_name() + ' ' +
                (' ' + self.arg_split_words[0] + ' ').join(text_args[1:]))

    def get_reverse(self, graph, args):
        '''Function to parse the graph and args and return the reverse
        function and args'''
        return None, []


class SayFunction(GraphFunction):
    '''Output all the following arguments [Actor, raw text]'''
    def __init__(self):
        super().__init__(
            function_name='say',
            possible_arg_nums=['ALL'],
            arg_split_words=[],
            arg_find_type=[{}],
            arg_constraints=[
                [],  # no constraints on the actor
            ],
            func_constraints=[],
            callback_triggers=[
                {'action': 'said', 'args': [0, 1]},
            ]
        )

    def func(self, graph, args):
        '''<Actor> sends message history to room [or specified <recipient>]'''
        actor = args[0]
        words = args[1].strip()
        if words.startswith('"') and words.endswith('"'):
            words = words[1:-1]
        room_id = graph.location(actor)
        agent_ids = graph.get_room_agents(room_id)
        said_action = {
            'caller': self.get_name(), 'name': 'said', 'room_id': room_id,
            'actors': [actor], 'present_agent_ids': agent_ids,
            'content': words,
        }
        graph.broadcast_to_room(said_action, exclude_agents=[actor])
        return True

    def format_observation(self, graph, viewing_agent, action,
                           telling_agent=None):
        '''Parse the observations to recount, then return them'''
        actor = action['actors'][0]
        content = action['content']
        if viewing_agent == actor:
            actor_text = 'You'
        else:
            actor_text = graph.node_to_desc(actor, use_the=True).capitalize()
        if content[-1] not in ['.', '?', '!']:
            content += '.'
        return '\n{} said "{}"\n'.format(actor_text, content)


class ShoutFunction(GraphFunction):
    '''Output all the following arguments [Actor, raw text]'''
    def __init__(self):
        super().__init__(
            function_name='shout',
            possible_arg_nums=['ALL'],
            arg_split_words=[],
            arg_find_type=[{}],
            arg_constraints=[
                [],  # no constraints on the actor
            ],
            func_constraints=[],
            callback_triggers=[
                {'action': 'shouted', 'args': [0, 1]},
            ]
        )

    def func(self, graph, args):
        '''<Actor> sends message history to room [or specified <recipient>]'''
        actor = args[0]
        words = args[1].strip()
        if words.startswith('"') and words.endswith('"'):
            words = words[1:-1]
        room_id = graph.location(actor)
        agent_ids = graph.get_room_agents(room_id)
        said_action = {
            'caller': self.get_name(), 'name': 'shouted', 'room_id': room_id,
            'actors': [actor], 'present_agent_ids': agent_ids,
            'content': words,
        }
        graph.broadcast_to_all_agents(said_action, exclude_agents=[actor])
        return True

    def format_observation(self, graph, viewing_agent, action,
                           telling_agent=None):
        '''Parse the observations to recount, then return them'''
        actor = action['actors'][0]
        content = action['content']
        if viewing_agent == actor:
            actor_text = 'You'
        else:
            actor_text = graph.node_to_desc(actor, use_the=True).capitalize()
        if content[-1] not in ['.', '?', '!']:
            content += '.'
        return '{} shouted "{}"\n'.format(actor_text, content)


class WhisperFunction(GraphFunction):
    '''Output all the following arguments [Actor, Target, raw text]'''
    def __init__(self):
        super().__init__(
            function_name='whisper',
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'sameloc+players', 'from': 0}],
            arg_constraints=[[], []],
            func_constraints=[],
            callback_triggers=[
                {'action': 'told', 'args': [0, 1, 2]},
            ]
        )

    def func(self, graph, args):
        '''<Actor> sends message history to room [or specified <recipient>]'''
        actor = args[0]
        words = args[2]
        room_id = graph.location(actor)
        agent_ids = graph.get_room_agents(room_id)
        said_action = {
            'caller': self.get_name(), 'name': 'said', 'room_id': room_id,
            'actors': args[:2], 'present_agent_ids': agent_ids,
            'content': words, 'target_agent': args[1],
        }
        graph.broadcast_to_room(said_action, exclude_agents=[actor])
        return True

    def format_observation(self, graph, viewing_agent, action,
                           telling_agent=None):
        '''Parse the observations to recount, then return them'''
        actor = action['actors'][0]
        target = action['actors'][1]
        content = action['content']
        involved = False
        if viewing_agent == actor:
            actor_text = 'You'
            involved = True
        else:
            actor_text = graph.node_to_desc(actor, use_the=True).capitalize()
        if viewing_agent == target:
            target_text = 'you'
            involved = True
        else:
            target_text = graph.node_to_desc(target, use_the=True)
        if involved:
            if content[-1] not in ['.', '?', '!']:
                content += '.'
            return '{} whispered {} "{}"\n'.format(actor_text, target_text, content)
        return '{} whispered something to {}.'.format(actor_text, target_text)

    def valid_args(self, graph, args):
        args = [a.lower() for a in args]
        loc = graph.location(args[0])
        try:
            # convert the arguments supplied to text form
            text_args = [graph.node_to_desc_raw(i, from_id=loc).lower()
                         for i in args[:2]]
            # ensure that those are valid from the parser perspective
            valid, args, _args = self.parse_descs_to_args(graph, text_args)
            if not valid:
                return False
            # ensure that they pass the function constraints
            valid, _cons_passed, _failure = self.evaluate_constraint_set(
                graph,
                args,
                self.func_constraints,
            )
            return valid
        except BaseException:
            return False

    def evaluate_constraint_set(self, graph, args, constraints):
        '''Can't talk to yourself, only constraint'''
        if args[0] == args[1]:
            return False, 0, {
                'caller': None,
                'room_id': self.location(args[0]),
                'txt': 'If you talk to yourself, you might seem crazy...',
            }
        return True, 0, None

    def parse_text_to_args(self, graph, actor_id, text):
        '''Breaks text into function arguments based on tell whispering "something"
        Returns:
        (None, display text, None) if parsing failed to find valid candidates
        (True, arg_ids, canonical_text_args) if parsing and constraints succeed
        (False, Failure action, matched_args)
                if parsing succeeds but constraints fail
        '''
        actor_id = actor_id.lower()
        descs = [actor_id]
        text = ' '.join(text)
        text = text.lower()
        if '"' not in text or not text.endswith('"'):
            return None, 'Be sure to use quotes to speak (").', None
        try:
            target = text.split('"')[0].strip()
            content = text.split('"')[1:]
            content = '"'.join(content).strip('"')
            descs = [actor_id, target]
            valid, arg_ids, c_args = self.parse_descs_to_args(graph, descs)
            if not valid:
                return None, "You don't know what you're talking to", None
            arg_ids.append(content)
            c_args.append(content)
            return valid, arg_ids, c_args
        except Exception:
            # import sys, traceback
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # traceback.print_tb(exc_traceback)
            # print(repr(e))
            # TODO the above in debug mode? would be useful
            return None, "You couldn't talk to that now", None

    def get_name(self):
        '''Get the canonical name of this function'''
        name = self.name
        if type(name) is list:
            name = name[0]
        return name

    def get_canonical_form(self, graph, args):
        '''Get canonical form for the given args on this function'''
        loc = graph.location(args[0])
        target_text = graph.node_to_desc_raw(args[1], from_id=loc)
        return 'whisper {} "{}"'.format(target_text, args[2])


class TellFunction(GraphFunction):
    '''Output all the following arguments [Actor, Target, raw text]'''
    def __init__(self):
        super().__init__(
            function_name='tell',
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'sameloc+players', 'from': 0}],
            arg_constraints=[[], []],
            func_constraints=[],
            callback_triggers=[
                {'action': 'told', 'args': [0, 1, 2]},
            ]
        )

    def func(self, graph, args):
        '''<Actor> sends message history to room [or specified <recipient>]'''
        actor = args[0]
        words = args[2]
        room_id = graph.location(actor)
        agent_ids = graph.get_room_agents(room_id)
        said_action = {
            'caller': self.get_name(), 'name': 'said', 'room_id': room_id,
            'actors': args[:2], 'present_agent_ids': agent_ids,
            'content': words, 'target_agent': args[1],
        }
        graph.broadcast_to_room(said_action, exclude_agents=[actor])
        return True

    def format_observation(self, graph, viewing_agent, action,
                           telling_agent=None):
        '''Parse the observations to recount, then return them'''
        actor = action['actors'][0]
        target = action['actors'][1]
        content = action['content']
        involved = False
        if viewing_agent == actor:
            actor_text = 'You'
            involved = True
        else:
            actor_text = graph.node_to_desc(actor, use_the=True).capitalize()
        if viewing_agent == target:
            target_text = 'you'
            involved = True
        else:
            target_text = graph.node_to_desc(target, use_the=True)
        if involved:
            if content[-1] not in ['.', '?', '!']:
                content += '.'
            return '{} told {} "{}"\n'.format(actor_text, target_text, content)
        #return '{} whispered something to {}.'.format(actor_text, target_text)
        return '{} told {} "{}"\n'.format(actor_text, target_text, content)

    def valid_args(self, graph, args):
        args = [a.lower() for a in args]
        loc = graph.location(args[0])
        try:
            # convert the arguments supplied to text form
            text_args = [graph.node_to_desc_raw(i, from_id=loc).lower()
                         for i in args[:2]]
            # ensure that those are valid from the parser perspective
            valid, args, _args = self.parse_descs_to_args(graph, text_args)
            if not valid:
                return False
            # ensure that they pass the function constraints
            valid, _cons_passed, _failure = self.evaluate_constraint_set(
                graph,
                args,
                self.func_constraints,
            )
            return valid
        except BaseException:
            return False

    def evaluate_constraint_set(self, graph, args, constraints):
        '''Can't talk to yourself, only constraint'''
        if args[0] == args[1]:
            return False, 0, {
                'caller': None,
                'room_id': self.location(args[0]),
                'txt': 'If you talk to yourself, you might seem crazy...',
            }
        return True, 0, None

    def parse_text_to_args(self, graph, actor_id, text):
        '''Breaks text into function arguments based on tell target "something"
        Returns:
        (None, display text, None) if parsing failed to find valid candidates
        (True, arg_ids, canonical_text_args) if parsing and constraints succeed
        (False, Failure action, matched_args)
                if parsing succeeds but constraints fail
        '''
        actor_id = actor_id.lower()
        descs = [actor_id]
        text = ' '.join(text)
        text = text.lower()
        if '"' not in text or not text.endswith('"'):
            return None, 'Be sure to use quotes to speak (").', None
        try:
            target = text.split('"')[0].strip()
            content = text.split('"')[1:]
            content = '"'.join(content).strip('"')
            descs = [actor_id, target]
            valid, arg_ids, c_args = self.parse_descs_to_args(graph, descs)
            if not valid:
                return None, "You don't know what you're talking to", None
            arg_ids.append(content)
            c_args.append(content)
            return valid, arg_ids, c_args
        except Exception:
            # import sys, traceback
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # traceback.print_tb(exc_traceback)
            # print(repr(e))
            # TODO the above in debug mode? would be useful
            return None, "You couldn't talk to that now", None

    def get_name(self):
        '''Get the canonical name of this function'''
        name = self.name
        if type(name) is list:
            name = name[0]
        return name

    def get_canonical_form(self, graph, args):
        '''Get canonical form for the given args on this function'''
        loc = graph.location(args[0])
        target_text = graph.node_to_desc_raw(args[1], from_id=loc)
        return 'tell {} "{}"'.format(target_text, args[2])


class RetellFunction(GraphFunction):
    '''Tell the world the last N actions that you've observed
    [Actor, optional recipient]
    '''
    ACTION_LIMIT = 5

    def __init__(self):
        super().__init__(
            function_name='retell',
            possible_arg_nums=[1, 2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'sameloc', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                [{'type': 'is_type', 'in_args': [1],
                  'args': [['agent'], 'You shouldn\'t talk to that.']}],
            ],
            func_constraints=[],
            callback_triggers=[
                {'action': 'told', 'args': [0, 1]},
            ]
        )
        self.formats = {'told': '{0} spoke to {1}.'}

    def func(self, graph, args):
        '''<Actor> sends message history to room [or specified <recipient>]'''
        telling_agent = args[0]
        room_id = graph.location(telling_agent)
        actions = graph.get_action_history(telling_agent)
        for act in actions:
            if 'told_actions' in act:
                # Don't retell a telling
                del act['told_actions']
        if len(actions) == 0:
            graph.send_msg(telling_agent, 'You have nothing to say.')
            return
        if len(args) == 2:
            receiving_agents = [args[1]]
        else:
            o = graph.node_contains(room_id)
            receiving_agents = [a for a in o if graph.get_prop(a, 'agent')
                                and a != telling_agent]
        action = {
            'caller': self.get_name(), 'name': 'told', 'room_id': room_id,
            'told_actions': actions[-5:],
            'telling_agent': telling_agent,
        }
        for agent in receiving_agents:
            telling = action.copy()
            telling['actors'] = [telling_agent, agent]
            graph.send_action(agent, telling)
        if len(args) == 2:
            target_desc = graph.node_to_desc(args[1], use_the=True)
        else:
            target_desc = 'everyone'
        graph.send_msg(telling_agent,
                       'You told {} what you remembered. '.format(target_desc))
        return True

    def format_observation(self, graph, viewing_agent, action,
                           telling_agent=None):
        '''Parse the observations to recount, then return them'''
        telling_agent = action['actors'][0]
        actions = action['told_actions']
        t = ''
        for new_action in actions:
            if ('present_agent_ids' in new_action
                    and viewing_agent in new_action['present_agent_ids']):
                continue  # Don't tell an agent something they see/saw
            if new_action['caller'] is None:
                t += new_action['txt']
            elif new_action['caller'] == self.get_name():
                t += super().format_observation(graph, viewing_agent,
                                                new_action, telling_agent)
            else:
                if viewing_agent in new_action['actors']:
                    continue  # Don't tell an agent something they've done
                try:
                    func_wrap = GRAPH_FUNCTIONS[new_action['caller']]
                except BaseException:
                    func_wrap = CONSTRAINTS[new_action['caller']]
                new_action['past'] = True
                t += func_wrap.format_observation(graph, viewing_agent,
                                                  new_action, telling_agent)
        if len(t) == 0:
            # Don't say anything
            return ''
        while t[-1] == '\n' or t[-1] == ' ':
            t = t[:-1]
        return '{} spoke to you and said: "{}"'.format(
            graph.node_to_desc(telling_agent, use_the=True).capitalize(), t
        )

    def get_reverse(self, graph, args):
        return False, []


class UseFunction(GraphFunction):
    def __init__(self):
        super().__init__(
            function_name='use',
            possible_arg_nums=[3],
            arg_split_words=['with'],
            arg_find_type=[{},  # no constraints on the actor
                           {'type': 'carrying', 'from': 0},
                           {'type': 'all+here', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                is_held_item(1),
                [{'type': 'is_type', 'in_args': [2],
                  'args': [['object'], 'Both have to be objects. ']}],
            ],
            func_constraints=[],
            callback_triggers=[
                {'action': 'agent_used_with', 'args': [0, 1, 2]},
            ]
        )
        self.formats = {'cant_use_with': "{0} couldn't find out how to "
                                         "use {1} with {2}. ",
                        'failed': '{0} couldn\'t do that. '}

    def get_find_fail_text(self, arg_idx):
        if arg_idx == 1:
            return "You don't seem to have that. "
        return 'That isn\'t here. '

    def func(self, graph, args):
        '''<Actor> uses <held object> with <other object>'''
        held_obj = args[1]
        callbacks = graph.get_prop(held_obj, 'callbacks', {})
        if 'use_with' in callbacks:
            rets = Callbacks.handle(graph, callbacks['use_with'], args)
            if False in rets:
                return False  # This action was unsuccessfully handled
            if True in rets:
                return True  # This action was successfully handled

        other_obj = args[2]
        callbacks = graph.get_prop(other_obj, 'callbacks', {})
        if 'use_with' in callbacks:
            rets = Callbacks.handle(graph, callbacks['use_with'], args)
            if False in rets:
                return False  # This action was unsuccessfully handled
            if True in rets:
                return True  # This action was successfully handled

        agent_id = args[0]
        room_id = graph.location(agent_id)
        cant_use_action = {'caller': self.get_name(), 'name': 'cant_use_with',
                           'room_id': room_id, 'actors': args}
        graph.send_action(args[0], cant_use_action)
        return False

    def get_action_observation_format(self, action, descs):
        if action['name'] == 'used_with':
            return '{0} {1} '
        return super().get_action_observation_format(action, descs)


class MoveAgentFunction(GraphFunction):
    '''[actor, destination room or path name from actor's room]'''
    def __init__(self):
        super().__init__(
            function_name='go',
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{},  # no constraints on the actor
                           {'type': 'path', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                [
                    {'type': 'is_type', 'in_args': [1], 'args': ['room']},
                    {'type': 'is_locked', 'in_args': [1], 'args': [False]},
                    {'type': 'not_location_of', 'in_args': [1], 'args': []},
                ]
            ],
            func_constraints=[
                {'type': 'fits_in', 'in_args': [0, 1], 'args': []},
            ],
            callback_triggers=[
                {'action': 'moved_to', 'args': [0, 1]},
                {'action': 'agent_entered', 'args': [0, 1]},
            ]
        )
        self.formats = {'left': '{0} left towards {1}. ',
                        'arrived': '{0} arrived from {1}. ',
                        'failed': '{0} can\'t do that. ',
                        'follow': '{0} follow. ',
                        'followed': '{0} followed {1} here.'}

    def follow_agent(self, graph, args, followed):
        '''handler for all following actions'''
        agent_id = args[0]
        old_room_id = graph.location(agent_id)
        agent = graph.oo_graph.get_node(agent_id)
        followers = agent.get_followers()
        room_id = args[1]
        leave_action = {'caller': self.get_name(), 'name': 'left',
                        'room_id': old_room_id,
                        'actors': [agent_id, room_id]}
        graph.broadcast_to_room(leave_action)
        graph.move_object(agent_id, room_id)

        # Prepare and send action for listing room contents
        agent = graph.oo_graph.get_node(agent_id)
        is_return = room_id in agent._visited_rooms
        if is_return or not graph.has_prop(room_id, 'first_desc'):
            if not graph.has_prop(room_id, 'short_desc'):
                room_desc = \
                    graph.get_prop(room_id, 'desc', None)
            else:
                room_desc = \
                    graph.get_prop(room_id, 'short_desc')
        else:
            room_desc = graph.get_prop(room_id, 'first_desc')
        if is_return:
            agent_ids, agent_descs = \
                graph.get_nondescribed_room_agents(room_id)
            object_ids, object_descs = \
                graph.get_nondescribed_room_objects(room_id)
            _room_ids, room_descs = graph.get_room_edges(room_id)
        else:
            agent_ids, agent_descs = [], []
            object_ids, object_descs = [], []
            room_descs = []
        list_room_action = {
            'caller': 'look', 'name': 'list_room', 'room_id': room_id,
            'actors': [args[0]], 'agent_ids': agent_ids,
            'present_agent_ids': agent_ids, 'object_ids': object_ids,
            'agent_descs': agent_descs, 'object_descs': object_descs,
            'room_descs': room_descs, 'room_desc': room_desc,
            'returned': is_return,
            'room_agents': graph.get_room_agents(room_id, drop_prefix=True),
        }
        graph.send_action(args[0], list_room_action)
        agent._last_rooms = old_room_id
        agent._visited_rooms.add(old_room_id)
        agent._visited_rooms.add(room_id)
        graph.npc_models.dialogue_clear_partner(agent_id)

        # Handle follows
        for other_agent in list(followers):
            other_agent = other_agent.node_id
            room2 = graph.location(other_agent)
            if old_room_id == room2:
                follow_action = {'caller': self.get_name(), 'name': 'follow',
                                 'room_id': old_room_id,
                                 'actors': [other_agent]}
                graph.send_msg(other_agent, 'You follow.\n', follow_action)
                new_args = args.copy()
                new_args[0] = other_agent
                self.follow_agent(graph, new_args, agent_id)

        # Now that everyone is here, handle arrivals
        arrive_action = {'caller': self.get_name(), 'name': 'followed',
                         'room_id': room_id,
                         'actors': [agent_id, followed]}
        graph.broadcast_to_room(arrive_action, exclude_agents=followers)
        Callbacks.handle_callbacks(self, graph, args)
        return True

    def func(self, graph, args):
        '''<Actor> moves to <location>'''
        agent_id = args[0]
        old_room_id = graph.location(agent_id)
        agent = graph.oo_graph.get_node(agent_id)
        followers = agent.get_followers()
        room_id = args[1]
        leave_action = {'caller': self.get_name(), 'name': 'left',
                        'room_id': old_room_id,
                        'actors': [agent_id, room_id],
                        'room_agents': graph.get_room_agents(room_id, drop_prefix=True)}
        graph.broadcast_to_room(leave_action)
        graph.move_object(agent_id, room_id)

        # Prepare and send action for listing room contents
        agent = graph.oo_graph.get_node(agent_id)
        is_return = room_id in agent._visited_rooms
        if is_return or not graph.has_prop(room_id, 'first_desc'):
            if not graph.has_prop(room_id, 'short_desc'):
                room_desc = \
                    graph.get_prop(room_id, 'desc', None)
            else:
                room_desc = \
                    graph.get_prop(room_id, 'short_desc')
        else:
            room_desc = graph.get_prop(room_id, 'first_desc')
        if is_return or not graph.has_prop(room_id, 'first_desc'):
            agent_ids, agent_descs = \
                graph.get_nondescribed_room_agents(room_id)
            object_ids, object_descs = \
                graph.get_nondescribed_room_objects(room_id)
            _room_ids, room_descs = graph.get_room_edges(room_id)
        else:
            agent_ids, agent_descs = [], []
            object_ids, object_descs = [], []
            room_descs = []
        list_room_action = {
            'caller': 'look', 'name': 'list_room', 'room_id': room_id,
            'actors': [args[0]], 'agent_ids': agent_ids,
            'present_agent_ids': agent_ids, 'object_ids': object_ids,
            'agent_descs': agent_descs, 'object_descs': object_descs,
            'room_descs': room_descs, 'room_desc': room_desc,
            'returned': is_return,
            'room_agents': graph.get_room_agents(room_id, drop_prefix=True),
        }
        graph.send_action(args[0], list_room_action)
        agent._last_rooms = old_room_id
        agent._visited_rooms.add(old_room_id)
        agent._visited_rooms.add(room_id)
        graph.npc_models.dialogue_clear_partner(agent_id)

        # Handle follows
        for other_agent in list(followers):
            room2 = graph.location(other_agent)
            if old_room_id == room2:
                follow_action = {'caller': self.get_name(), 'name': 'follow',
                                 'room_id': old_room_id,
                                 'actors': [other_agent]}
                graph.send_msg(other_agent, 'You follow.\n', follow_action)
                new_args = args.copy()
                new_args[0] = other_agent
                self.follow_agent(graph, new_args, agent_id)

        # Now that everyone is here, handle arrivals
        arrive_action = {'caller': self.get_name(), 'name': 'arrived',
                         'room_id': room_id,
                         'actors': [agent_id, old_room_id],
                         'room_agents': graph.get_room_agents(room_id, drop_prefix=True)}
        graph.broadcast_to_room(arrive_action, exclude_agents=followers)
        return True

    def parse_text_to_args(self, graph, actor_id, text):
        '''Wraps the super parse_text_to_args to be able to handle the special
        case of "go back"
        '''
        actor_id = actor_id.lower()
        if len(text) == 0:
            return super().parse_text_to_args(graph, actor_id, text)
        elif text[-1].lower() == 'back':
            agent = graph.oo_graph.get_node(actor_id)
            if agent._last_rooms is None:
                return None, 'Back where exactly? You\'ve just started!', None
            text[-1] = graph.node_to_desc_raw(
                agent._last_rooms, from_id=graph.location(actor_id))
        return super().parse_text_to_args(graph, actor_id, text)

    def get_find_fail_text(self, arg_idx):
        return 'Where is that? You don\'t see it'

    def get_action_observation_format(self, action, descs):
        if 'past' not in action:
            if descs[0] == 'You':
                return ''  # Don't tell someone where they just went
        return super().get_action_observation_format(action, descs)

    REPLACEMENTS = {'e': 'east', 'w': 'west', 'n': 'north', 's': 'south',
                    'u': 'up', 'd': 'down'}

    def parse_descs_to_args(self, graph, args):
        # Replace shortcuts with full words for better matching
        if args[1] in self.REPLACEMENTS:
            args[1] = self.REPLACEMENTS[args[1]]
        return super().parse_descs_to_args(graph, args)

    # TODO implement reverse for go


class FollowFunction(GraphFunction):
    '''[Actor, agent actor should follow in same room]'''
    def __init__(self):
        super().__init__(
            function_name=['follow'],
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'sameloc', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                [{'type': 'is_type', 'in_args': [1],
                  'args': [['agent'], 'You can\'t follow that.']}],
            ],
            func_constraints=[],
            callback_triggers=[
                {'action': 'followed', 'args': [0, 1]},
            ]
        )
        self.formats = {'followed': '{0} started following {1}. ',
                        'failed': '{0} couldn\'t follow that. '}

    def func(self, graph, args):
        '''<actor> start following [<agent>] (unfollow if no agent supplied)'''
        agent_id = args[0]
        room_id = graph.location(args[0])
        following = graph.get_following(agent_id)

        if len(args) > 1 and following == args[1]:
            graph.send_msg(agent_id, 'You are already following them.\n')
            return True

        # Have to unfollow if currently following someone
        if following is not None:
            GRAPH_FUNCTIONS['unfollow'].handle(graph, [args[0]])

        graph.set_follow(agent_id, args[1])
        follow_action = {
            'caller': self.get_name(), 'name': 'followed',
            'room_id': room_id, 'actors': args,
        }
        graph.broadcast_to_room(follow_action)
        return True

    def get_reverse(self, graph, args):
        return 'unfollow', [args[0]]


class HitFunction(GraphFunction):
    '''[Actor, victim in same room]'''
    def __init__(self):
        super().__init__(
            function_name=['hit'],
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'sameloc', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                [{'type': 'is_type', 'in_args': [1],
                  'args': [['agent'], 'You can\'t hit that.']},
                 {'type': 'not_type', 'in_args': [1],
                  'args': [['described'], 'You decide against attacking.']}],
            ],
            func_constraints=[],
            callback_triggers=[{'action': 'hit', 'args': [0, 1]}]
        )
        self.formats = {'attacked': '{0} attacked {1}. ',
                        'missed': '{0} attacked {1}, but missed. ',
                        'blocked': '{0} attacked {1}, but '
                                   '{1} blocked the attack. ',
                        'failed': '{0} couldn\'t hit that. '}

    def handle(self, graph, args):
        if Callbacks.try_overrides(self, graph, args):
            return True
        is_constrained, _cons_passed, failure_action = \
            self.evaluate_constraint_set(graph, args, self.func_constraints)
        if not is_constrained:
            func_failure_action = self.get_failure_action(graph, args)
            # What failed?
            graph.send_action(args[0], func_failure_action)
            # Why it failed
            graph.send_action(args[0], failure_action)
            return False
        is_successful = self.func(graph, args)
        return is_successful

    def func(self, graph, args):
        '''<Actor> attempts attack on <enemy>'''
        agent_id = args[0]
        room_id = graph.location(args[0])
        victim_id = args[1]
        damage = graph.get_prop(agent_id, 'damage', 0)
        armor = graph.get_prop(victim_id, 'defense', 0)
        attack = random.randint(0, damage + 1)
        defend = random.randint(0, armor)
        action = {
            'caller': self.get_name(), 'room_id': room_id, 'actors': args,
        }
        did_hit = False
        if damage == -1:  # It's not a very physical class
            if random.randint(0, 1):
                did_hit = True
                action['name'] = 'attacked'
                attack = 0
                defend = 0
            else:
                action['name'] = 'missed'
        elif (attack == 0 or attack - defend < 1) and not graph.freeze():
            action['name'] = 'missed' if attack == 0 else 'blocked'
        else:
            did_hit = True
            action['name'] = 'attacked'

        graph.broadcast_to_room(action)

        if did_hit:
            Callbacks.handle_callbacks(self, graph, args)
            # TODO move energy updates to a shared function
            energy = graph.get_prop(victim_id, 'health')
            energy = max(0, energy - (attack - defend))
            graph.set_prop(victim_id, 'health', energy)
            if energy <= 0:
                graph.die(victim_id)
            elif energy < 4 and energy > 0:
                # TODO move getting a health action to the health function
                health_text = graph.health(victim_id)
                my_health_action = {'caller': 'health', 'actors': [victim_id],
                                    'name': 'display_health',
                                    'room_id': room_id,
                                    'add_descs': [health_text]}
                graph.send_action(victim_id, my_health_action)
        else:
            Callbacks.handle_miss_callbacks(self, graph, args)
        return True

    def get_find_fail_text(self, arg_idx):
        return 'Where are they? You don\'t see them'


class HugFunction(GraphFunction):
    '''[Actor, target in same room]'''
    def __init__(self):
        super().__init__(
            function_name=['hug'],
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'sameloc', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                [{'type': 'is_type', 'in_args': [1],
                  'args': [['agent'], 'You can\'t hug that.']}],
            ],
            func_constraints=[],
            callback_triggers=[{'action': 'hug', 'args': [0, 1]}]
        )
        self.formats = {'hug': '{0} hugged {1}. ',
                        'failed': '{0} couldn\'t hug that. '}

    def func(self, graph, args):
        '''<Actor> hugs <target>'''
        room_id = graph.location(args[0])
        action = {
            'caller': self.get_name(), 'room_id': room_id, 'actors': args,
            'name': 'hug',
        }
        graph.broadcast_to_room(action)
        return True

    def get_find_fail_text(self, arg_idx):
        return 'Where are they? You don\'t see them'

    def get_reverse(self, graph, args):
        return False, []


class GetObjectFunction(GraphFunction):
    '''[Actor, object attainable by actor, optional container for object]'''
    def __init__(self):
        super().__init__(
            function_name=['get', 'take'],
            possible_arg_nums=[2, 3],
            arg_split_words=['from'],
            arg_find_type=[
                [{}, {}],  # no constraints on the actor
                [{'type': 'all+here', 'from': 0},
                 {'type': 'carrying', 'from': 2}],
                [{'type': 'contains', 'from': 1},
                 {'type': 'all+here', 'from': 0}],
            ],
            arg_constraints=[
                [],  # no constraints on the actor
                [{'type': 'is_type', 'in_args': [1], 'args': ['object']},
                 {'type': 'not_type', 'in_args': [1],
                  'args': [['not_gettable'], "That isn't something you can get"]},
                 {'type': 'not_type', 'in_args': [1],
                  'args': [['described'], "You choose not to take that and ruin this room's description"]}],
                [{'type': 'is_type', 'in_args': [2],
                  'args': [['container', 'room'], 'That\'s not a container.']},
                 {'type': 'is_locked', 'in_args': [2], 'args': [False]}],
            ],
            func_constraints=[
                {'type': 'fits_in', 'in_args': [1, 0], 'args': [],
                 'spec_fail': 'cant_carry'},
            ],
            callback_triggers=[
                {'action': 'moved_to', 'args': [1, 0]},
                {'action': 'agent_got', 'args': [0, 1]},
            ]
        )
        self.formats = {'got': '{0} got {1}. ',
                        'got_from': '{0} got {1} from {2}. ',
                        'failed': '{0} couldn\'t get {1}. '}

    def func(self, graph, args):
        '''<Actor> gets <item> [from <container>]'''
        agent_id, object_id = args[0], args[1]
        container_id = graph.location(object_id)
        room_id = graph.location(agent_id)
        graph.move_object(object_id, agent_id)
        if 'room' in graph.get_prop(container_id, 'classes'):
            get_action = {'caller': self.get_name(), 'name': 'got',
                          'room_id': room_id,
                          'actors': [agent_id, object_id]}
        else:
            get_action = {'caller': self.get_name(), 'name': 'got_from',
                          'room_id': room_id,
                          'actors': [agent_id, object_id, container_id]}
        graph.broadcast_to_room(get_action)
        return True

    def get_find_fail_text(self, arg_idx):
        if arg_idx == 2:
            return 'That isn\'t there. '
        else:
            return 'That isn\'t here. '

    def parse_descs_to_args(self, graph, args):
        # Append a location for the object, defaulting to the room if the
        # immediate container of something can't be found
        args = [a.lower() for a in args]
        if len(args) < 3:
            try:
                object_ids = graph.desc_to_nodes(args[1], args[0], 'all+here')
                i = 0
                container_id = args[0]
                # avoid reflexive matches!
                while container_id == args[0]:
                    container_id = graph.location(object_ids[i])
                    i += 1
                container_name = graph.node_to_desc_raw(container_id)
                args.append(container_name)
            except Exception:
                args.append(graph.node_to_desc_raw(graph.location(args[0])))
        return super().parse_descs_to_args(graph, args)

    def get_canonical_form(self, graph, args):
        '''Get canonical form for the given args on this function'''
        if len(args) == 3 and graph.get_prop(args[2], 'container') is True:
            return super().get_canonical_form(graph, args)
        else:
            return super().get_canonical_form(graph, args[:2])

    def get_reverse(self, graph, args):
        if graph.get_prop(args[2], 'container') is True:
            return 'put', args
        else:
            return 'drop', args[:2]


# TODO override get_canonical_form for on/in
class PutObjectInFunction(GraphFunction):
    '''[Actor, object actor is carrying, container]'''
    def __init__(self):
        super().__init__(
            function_name='put',
            possible_arg_nums=[3],
            arg_split_words=['in', 'into', 'on', 'onto'],
            arg_find_type=[{},  # no constraints on the actor
                           {'type': 'carrying', 'from': 0},
                           {'type': 'all+here', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                is_held_item(1),
                [{'type': 'is_type', 'in_args': [2],
                  'args': [['container'], 'That\'s not a container.']}],
            ],
            func_constraints=[
                {'type': 'fits_in', 'in_args': [1, 2], 'args': []},
            ],
            callback_triggers=[
                {'action': 'moved_to', 'args': [1, 2]},
                {'action': 'agent_put_in', 'args': [0, 1, 2]},
            ]
        )
        self.formats = {'put_in': '{0} put {1} into {2}. ',
                        'put_on': '{0} put {1} onto {2}. ',
                        'failed': '{0} couldn\'t put that. '}

    def func(self, graph, args):
        '''<Actor> puts <object> in or on <container>'''
        agent_id, object_id, container_id = args[0], args[1], args[2]
        graph.move_object(object_id, container_id)
        act_name = 'put_' + graph.get_prop(container_id, 'surface_type', 'in')
        room_id = graph.location(agent_id)
        put_action = {'caller': self.get_name(), 'name': act_name,
                      'room_id': room_id,
                      'actors': [agent_id, object_id, container_id]}
        graph.broadcast_to_room(put_action)
        return True

    def get_find_fail_text(self, arg_idx):
        if arg_idx == 1:
            return 'You don\'t have that. '
        else:
            return 'That isn\'t here. '

    def get_reverse(self, graph, args):
        return 'get', args


class DropObjectFunction(GraphFunction):
    '''[Actor, object actor is carrying]'''
    def __init__(self):
        super().__init__(
            function_name='drop',
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{},  # no constraints on the actor
                           {'type': 'carrying', 'from': 0},
                           {'type': 'all+here', 'from': 0}],
            arg_constraints=[[], is_held_item(1), []],
            func_constraints=[
                {'type': 'fits_in', 'in_args': [1, 2], 'args': []},
            ],
            callback_triggers=[
                {'action': 'moved_to', 'args': [1, 2]},
                {'action': 'agent_dropped', 'args': [0, 1]},
            ]
        )
        self.formats = {'dropped': '{0} dropped {1}. ',
                        'failed': '{0} couldn\'t drop that. '}

    def func(self, graph, args):
        '''<Actor> drops <object>'''
        agent_id, object_id, room_id = args[0], args[1], args[2]
        graph.move_object(object_id, room_id)
        put_action = {'caller': self.get_name(), 'name': 'dropped',
                      'room_id': room_id, 'actors': [agent_id, object_id]}
        graph.broadcast_to_room(put_action)
        return True

    def get_find_fail_text(self, arg_idx):
        return 'You don\'t have that. '

    def parse_descs_to_args(self, graph, args):
        # appends the room as the target of the move
        args.append(graph.node_to_desc_raw(graph.location(args[0])))
        return super().parse_descs_to_args(graph, args)

    def get_reverse(self, graph, args):
        return 'get', args


class GiveObjectFunction(GraphFunction):
    '''[Actor, object actor is carrying, other agent in same room]'''
    def __init__(self):
        super().__init__(
            function_name='give',
            possible_arg_nums=[3],
            arg_split_words=['to'],
            arg_find_type=[{},  # no constraints on the actor
                           {'type': 'carrying', 'from': 0},
                           {'type': 'sameloc', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                is_held_item(1),
                [{'type': 'is_type', 'in_args': [2],
                  'args': [['agent'], 'The recipient is a thing.']}],
            ],
            func_constraints=[
                {'type': 'fits_in', 'in_args': [1, 2], 'args': [],
                 'spec_fail': 'cant_carry'},
            ],
            callback_triggers=[
                {'action': 'moved_to', 'args': [1, 2]},
                {'action': 'agent_received_from', 'args': [2, 1, 0]},
            ]
        )
        self.formats = {'gave': '{0} gave {2} {1}. ',
                        'failed': '{0} couldn\'t give that. '}

    def func(self, graph, args):
        '''<Actor> gives <object> to <agent>'''
        agent_id, object_id, receiver_id = args[0], args[1], args[2]
        graph.move_object(object_id, receiver_id)
        room_id = graph.location(agent_id)
        give_action = {'caller': self.get_name(), 'name': 'gave',
                       'room_id': room_id,
                       'actors': [agent_id, object_id, receiver_id]}
        graph.broadcast_to_room(give_action)
        return True

    def get_find_fail_text(self, arg_idx):
        if arg_idx == 1:
            return 'You don\'t have that. '
        else:
            return 'They aren\'t here. '

    def get_reverse(self, graph, args):
        return 'steal', args


class StealObjectFunction(GraphFunction):
    '''[Actor, object other agent is carrying, other agent in same room]'''
    def __init__(self):
        super().__init__(
            function_name='steal',
            possible_arg_nums=[2, 3],
            arg_split_words=['from'],
            arg_find_type=[
                [{}, {}],  # no constraints on the actor
                [{'type': 'all+here', 'from': 0},
                 {'type': 'carrying', 'from': 2}],
                [{'type': 'contains', 'from': 1},
                 {'type': 'all+here', 'from': 0}],
            ],
            arg_constraints=[
                [],  # no constraints on the actor
                is_held_item(1),
                [{'type': 'is_type', 'in_args': [2],
                  'args': [['agent'],
                           'You can\'t steal from that.']}],
            ],
            func_constraints=[
                {'type': 'fits_in', 'in_args': [1, 0], 'args': [],
                 'spec_fail': 'cant_carry'},
            ],
            callback_triggers=[
                {'action': 'moved_to', 'args': [1, 0]},
                {'action': 'agent_stole_from', 'args': [0, 1, 2]},
            ]
        )
        self.formats = {'stole': '{0} stole {1} from {2}. ',
                        'failed': '{0} couldn\'t give that. '}

    def func(self, graph, args):
        '''<Actor> steals <object> from <agent>'''
        agent_id, object_id, victim_id = args[0], args[1], args[2]
        graph.move_object(object_id, agent_id)
        room_id = graph.location(agent_id)
        give_action = {'caller': self.get_name(), 'name': 'stole',
                       'room_id': room_id,
                       'actors': [agent_id, object_id, victim_id]}
        graph.broadcast_to_room(give_action)
        return True

    def parse_descs_to_args(self, graph, args):
        # Append a location for the object, defaulting to the room if the
        # immediate container of something can't be found
        args = [a.lower() for a in args]
        if len(args) < 3:
            try:
                object_ids = graph.desc_to_nodes(args[1], args[0], 'all+here')
                i = 0
                container_id = args[0]
                # avoid reflexive matches!
                while container_id == args[0]:
                    container_id = graph.location(object_ids[i])
                    i += 1
                container_name = graph.node_to_desc_raw(container_id)
                args.append(container_name)
            except Exception:
                args.append(graph.node_to_desc_raw(graph.location(args[0])))
        return super().parse_descs_to_args(graph, args)

    def get_find_fail_text(self, arg_idx):
        if arg_idx == 1:
            return 'They don\'t have that. '
        else:
            return 'They aren\'t here. '

    def get_reverse(self, graph, args):
        return 'give', args


class EquipObjectFunction(GraphFunction):
    '''[Actor, object actor is carrying]'''
    def __init__(self, function_name='equip', action='equipped',
                 additional_constraints=None):
        if additional_constraints is None:
            additional_constraints = []
        super().__init__(
            function_name=function_name,
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'carrying', 'from': 0}],
            arg_constraints=[[], is_held_item(1) + additional_constraints],
            func_constraints=[],
            callback_triggers=[
                {'action': 'agent_' + action, 'args': [0, 1]},
                {'action': action + '_by', 'args': [1, 0]},
            ]
        )
        self.formats = {action: '{0} ' + action + ' {1}. ',
                        'failed': '{0} couldn\'t ' + function_name + ' that. '}
        self.action = action

    def func(self, graph, args):
        '''<Agent> equips <object>'''
        agent_id, object_id = args[0], args[1]
        graph.set_prop(object_id, 'equipped', self.name)
        for n, s in graph.get_prop(object_id, 'stats', {'defense': 1}).items():
            graph.inc_prop(agent_id, n, s)
        room_id = graph.location(agent_id)
        equip_action = {'caller': self.get_name(), 'name': self.action,
                        'room_id': room_id, 'actors': [agent_id, object_id]}
        graph.broadcast_to_room(equip_action)
        return True

    def get_find_fail_text(self, arg_idx):
        return 'You don\'t have that.'

    def get_reverse(self, graph, args):
        return 'remove', args


class WearObjectFunction(EquipObjectFunction):
    '''[Actor, object actor is carrying]'''
    def __init__(self):
        super().__init__(
            function_name='wear', action='wore',
            additional_constraints=[
                {'type': 'is_type', 'in_args': [1],
                 'args': [['wearable'], 'That isn\'t wearable.']}
            ]
        )


class WieldObjectFunction(EquipObjectFunction):
    '''[Actor, object actor is carrying]'''
    def __init__(self):
        super().__init__(
            function_name='wield', action='wielded',
            additional_constraints=[
                {'type': 'is_type', 'in_args': [1],
                 'args': [['weapon'], 'That isn\'t wieldable.']}
            ]
        )


class RemoveObjectFunction(GraphFunction):
    '''[Actor, object actor is carrying]'''
    def __init__(self):
        super().__init__(
            function_name=['remove', 'unwield'],
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'carrying', 'from': 0}],
            arg_constraints=[[], is_equipped_item(1)],
            func_constraints=[],
            callback_triggers=[
                {'action': 'agent_removed', 'args': [0, 1]},
                {'action': 'removed_by', 'args': [1, 0]},
            ]
        )
        self.formats = {'removed': '{0} removed {1}. ',
                        'failed': '{0} couldn\'t remove that. '}

    def func(self, graph, args):
        '''<Actor> unequips <object>'''
        agent_id, object_id = args[0], args[1]
        graph.set_prop(object_id, 'equipped', None)
        for n, s in graph.get_prop(object_id, 'stats', {'defense': 1}).items():
            graph.inc_prop(agent_id, n, -s)
        room_id = graph.location(agent_id)
        put_action = {'caller': self.get_name(), 'name': 'removed',
                      'room_id': room_id, 'actors': [agent_id, object_id]}
        graph.broadcast_to_room(put_action)
        return True

    def get_find_fail_text(self, arg_idx):
        return 'You don\'t have that equipped.'

    def get_reverse(self, graph, args):
        return 'equip', args


class IngestFunction(GraphFunction):
    '''[Actor, object actor is carrying]'''
    def __init__(self, function_name='ingest', action='ingested',
                 additional_constraints=None):
        if additional_constraints is None:
            additional_constraints = []
        super().__init__(
            function_name=function_name,
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'carrying', 'from': 0}],
            arg_constraints=[[], is_held_item(1) + additional_constraints],
            func_constraints=[],
            callback_triggers=[
                {'action': 'agent_' + action, 'args': [0, 1]},
                {'action': action + '_by', 'args': [1, 0]},
            ]
        )
        self.formats = {action: '{0} ' + action + ' {1}. ',
                        'failed': '{0} couldn\'t ' + function_name + ' that. '}
        self.action = action

    def func(self, graph, args):
        '''<Actor> consumes <object>'''
        agent_id, object_id = args[0], args[1]
        fe = graph.get_prop(object_id, 'food_energy')
        thing_desc = graph.node_to_desc(object_id, use_the=True)
        room_id = graph.location(agent_id)
        graph.delete_node(object_id)
        ingest_action = {'caller': self.get_name(), 'name': self.action,
                         'room_id': room_id, 'actors': [agent_id],
                         'add_descs': [thing_desc]}
        graph.broadcast_to_room(ingest_action)
        if fe >= 0:
            graph.send_msg(agent_id, "Yum.\n")
        else:
            graph.send_msg(agent_id, "Gross!\n")

        energy = graph.get_prop(agent_id, 'health')
        if energy < 8:
            prev_health = graph.health(agent_id)
            energy = energy + fe
            graph.set_prop(agent_id, 'health', energy)
            new_health = graph.health(agent_id)
            if energy <= 0:
                self.die(agent_id)
            elif prev_health != new_health:
                health_action = {'caller': 'health', 'name': 'changed',
                                 'room_id': room_id, 'actors': [args[0]],
                                 'add_descs': [prev_health, new_health]}
                graph.broadcast_to_room(health_action)
        return True

    def get_find_fail_text(self, arg_idx):
        return 'You don\'t have that.'


class EatFunction(IngestFunction):
    '''[Actor, object actor is carrying]'''
    def __init__(self):
        super().__init__(
            function_name='eat', action='ate',
            additional_constraints=[
                {'type': 'is_type', 'in_args': [1],
                 'args': [['food'], 'That isn\'t food.']}
            ]
        )


class DrinkFunction(IngestFunction):
    '''[Actor, object actor is carrying]'''
    def __init__(self):
        super().__init__(
            function_name='drink', action='drank',
            additional_constraints=[
                {'type': 'is_type', 'in_args': [1],
                 'args': [['drink'], 'That isn\'t a drink.']}
            ]
        )


class LockFunction(GraphFunction):
    '''[Actor, lockable thing in same location, key actor is carrying]'''
    def __init__(self):
        super().__init__(
            function_name='lock',
            possible_arg_nums=[3],
            arg_split_words=['with'],
            arg_find_type=[{},  # no constraints on the actor
                           {'type': 'all+here', 'from': 0},
                           {'type': 'carrying', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                [{'type': 'is_lockable', 'in_args': [1], 'args':[True]}],
                [{'type': 'is_type', 'in_args': [2],
                  'args': [['key'], 'That isn\'t a key.']}],
            ],
            func_constraints=[
                {'type': 'is_locked', 'in_args': [1], 'args':[False]},
                {'type': 'locked_with', 'in_args': [1, 2], 'args':[]},
            ],
            callback_triggers=[{'action': 'agent_unlocked', 'args': [0, 1]}]
        )
        self.formats = {'locked': '{0} locked {1}. ',
                        'failed': '{0} couldn\'t lock that. '}

    def get_improper_args_text(self, num_args):
        if num_args == 2:
            return 'Lock that with what?'
        else:
            return 'Lock is used with "lock <object/path> with <key>"'

    def func(self, graph, args):
        '''<Actor> locks <object> using <key>'''
        actor_id, target_id, key_id = args[0], args[1], args[2]
        room_id = graph.location(actor_id)
        if 'room' in graph.get_prop(target_id, 'classes'):
            graph.lock_path(graph.location(actor_id), target_id, key_id)
        else:
            # TODO implement lock_object
            graph.lock_object(target_id, key_id)
        lock_action = {'caller': self.get_name(), 'name': 'locked',
                       'room_id': room_id, 'actors': [actor_id, target_id]}
        graph.broadcast_to_room(lock_action)
        return True

    def get_reverse(self, graph, args):
        return 'lock', args


class UnlockFunction(GraphFunction):
    '''[Actor, lockable thing in same location, key actor is carrying]'''
    def __init__(self):
        super().__init__(
            function_name='unlock',
            possible_arg_nums=[3],
            arg_split_words=['with'],
            arg_find_type=[{},  # no constraints on the actor
                           {'type': 'all+here', 'from': 0},
                           {'type': 'carrying', 'from': 0}],
            arg_constraints=[
                [],  # no constraints on the actor
                [{'type': 'is_lockable', 'in_args': [1], 'args':[True]}],
                [{'type': 'is_type', 'in_args': [2],
                  'args': [['key'], 'That isn\'t a key.']}],
            ],
            func_constraints=[
                {'type': 'is_locked', 'in_args': [1], 'args':[True]},
                {'type': 'locked_with', 'in_args': [1, 2], 'args':[]},
            ],
            callback_triggers=[{'action': 'agent_unlocked', 'args': [0, 1]}]
        )
        self.formats = {'unlocked': '{0} unlocked {1}. ',
                        'failed': '{0} couldn\'t unlock that. '}

    def func(self, graph, args):
        '''<Actor> unlocks <object> using <key>'''
        actor_id, target_id, key_id = args[0], args[1], args[2]
        room_id = graph.location(actor_id)
        if 'room' in graph.get_prop(target_id, 'classes'):
            graph.unlock_path(graph.location(actor_id), target_id, key_id)
        else:
            # TODO implement unlock_object
            graph.unlock_object(target_id, key_id)
        lock_action = {'caller': self.get_name(), 'name': 'unlocked',
                       'room_id': room_id, 'actors': [actor_id, target_id]}
        graph.broadcast_to_room(lock_action)
        return True

    def get_improper_args_text(self, num_args):
        if num_args == 2:
            return 'Unlock that with what?'
        else:
            return 'Unlock is used with "unlock <object/path> with <key>"'

    def get_reverse(self, graph, args):
        return 'lock', args


class ExamineFunction(GraphFunction):
    '''[Actor, anything accessible to the actor]'''
    def __init__(self):
        super().__init__(
            function_name=['examine', 'ex'],
            possible_arg_nums=[2],
            arg_split_words=[],
            arg_find_type=[{}, {'type': 'all+here', 'from': 0}],
            arg_constraints=[[], []],
            func_constraints=[],
            callback_triggers=[{'action': 'agent_examined', 'args': [0, 1]}]
        )

    def func(self, graph, args):
        '''<Actor> examines <thing>'''
        agent_id, object_id = args[0], args[1]
        room_id = graph.location(agent_id)
        examine_action = {'caller': self.get_name(), 'name': 'witnessed',
                          'room_id': room_id, 'actors': [agent_id, object_id]}
        graph.broadcast_to_room(examine_action, [agent_id])

        if 'room' in graph.get_prop(object_id, 'classes'):
            object_type = 'room'
            add_descs = [graph.view.get_path_ex_desc(room_id, object_id, agent_id)]
        elif 'container' in graph.get_prop(object_id, 'classes'):
            # Mark containers as being examined so that they can be added
            # to the pool of all+here
            graph.set_prop(object_id, 'examined', True)
            object_type = 'container'
            add_descs = []
            add_descs.append(
                graph.get_prop(object_id, 'desc')
            )
            if len(graph.node_contains(object_id)) > 0:
                add_descs.append(graph.display_node(object_id))
        elif 'agent' in graph.get_prop(object_id, 'classes'):
            graph.set_prop(object_id, 'examined', True)
            object_type = 'agent'
            add_descs = []
            inv_txt = graph.get_inventory_text_for(object_id, give_empty=False)
            if graph.has_prop(object_id, 'desc'):
                add_descs.append(
                    graph.get_prop(object_id, 'desc')
                )
            if inv_txt != '':
                object_desc = graph.node_to_desc(object_id,
                                                 use_the=True).capitalize()
                add_descs.append(object_desc + ' is ' + inv_txt)
        else:
            object_type = 'object'
            add_descs = [graph.get_prop(object_id, 'desc')]
        if len(add_descs) == 0 or add_descs[0] is None or type(add_descs[0])==list:
            add_descs = ['There is nothing special about it. ']
        add_descs = ['\n'.join(add_descs)]  # Compress the descriptions to one
        examine_object_action = {
            'caller': self.get_name(), 'name': 'examine_object',
            'room_id': room_id, 'actors': args, 'add_descs': add_descs,
            'object_type': object_type
        }
        graph.send_action(agent_id, examine_object_action)
        return True

    def get_action_observation_format(self, action, descs):
        if action['name'] == 'witnessed':
            return '{0} looked at {1}. '
        elif action['name'] == 'examine_object':
            if 'past' in action:
                return '{0} examined {1}.\n{2}'
            else:
                return '{2}'
        return super().get_action_observation_format(action, descs)

    def get_find_fail_text(self, arg_idx):
        return 'That isn\'t here. '

    def get_improper_args_text(self, num_args):
        if num_args == 1:
            return 'Examine what?'
        else:
            return 'Examine is used as "examine <thing>"'

    def get_reverse(self, graph, args):
        return False, args


class SoloFunction(GraphFunction):
    '''[Actor]'''
    def __init__(self, function_name, callback_triggers):
        super().__init__(
            function_name=function_name,
            possible_arg_nums=[1],
            arg_split_words=[],
            arg_find_type=[{}],
            arg_constraints=[[]],
            func_constraints=[],
            callback_triggers=callback_triggers
        )

    def get_reverse(self, graph, args):
        return False, args


class EmoteFunction(SoloFunction):
    '''Output all the following arguments [Actor, raw text]'''
    def __init__(self, name):
        super().__init__(
            function_name=name,
            callback_triggers=[
                {'action': name, 'args': [0]},
            ]
        )
        self.desc = {
            'applaud':'applauds', 'blush':'blushes',
            'cry':'cries', 'dance':'dances', 'frown':'frowns', 'gasp':'gasps',
            'grin':'grins', 'groan':'groans',
            'growl':'growls', 'laugh':'laughs',
            'nod':'nods', 'nudge':'nudges', 'ponder':'ponders', 'pout':'pouts',
            'scream':'screams',
            'shrug':'shrugs', 'sigh':'sighs',
            'smile':'smiles', 'stare':'stares',
            'wave':'waves', 'wink':'winks', 'yawn':'yawns'
        }


    def func(self, graph, args):
        '''<Actor> sends message history to room [or specified <recipient>]'''
        actor = args[0]
        room_id = graph.location(actor)
        agent_ids = graph.get_room_agents(room_id)
        said_action = {
            'caller': self.get_name(), 'name': self.name, 'room_id': room_id,
            'actors': [actor], 'present_agent_ids': agent_ids,
            'content': self.desc[self.name],
        }
        #graph.broadcast_to_all_agents(said_action) #, exclude_agents=[actor])
        graph.broadcast_to_room(said_action) #, exclude_agents=[actor])
        return True

    def format_observation(self, graph, viewing_agent, action,
                           telling_agent=None):
        '''Parse the observations to recount, then return them'''
        actor = action['actors'][0]
        content = action['content']
        if viewing_agent == actor:
            actor_text = 'You'
            content = action['name']
        else:
            actor_text = graph.node_to_desc(actor, use_the=True).capitalize()
        if content[-1] not in ['.', '?', '!']:
            content += '.'
        return '{} {}\n'.format(actor_text, content)


class WaitFunction(SoloFunction):
    def __init__(self):
        super().__init__(
            function_name='wait',
            callback_triggers=[
                {'action': 'agent_waited', 'args': [0]},
            ]
        )
        self.formats = {'waited': '{0} waited. '}

    def func(self, graph, args):
        room_id = graph.location(args[0])
        graph.send_action(
            args[0],
            {'caller': self.get_name(), 'name': 'waited',
             'room_id': room_id, 'actors': [args[0]]}
        )
        return True


class InventoryFunction(SoloFunction):
    def __init__(self):
        super().__init__(
            function_name=['inventory', 'inv', 'i'],
            callback_triggers=[
                {'action': 'check_inventory', 'args': [0]},
            ]
        )

    def get_action_observation_format(self, action, descs):
        if action['name'] == 'check_inventory':
            if descs[0] == 'You':
                return 'You checked your inventory. '
            elif descs[0] == 'I':
                return 'I checked my inventory'
            else:
                return '{0} checked their inventory. '
        elif action['name'] == 'list_inventory':
            if 'past' in action:
                if descs[0] == 'You':
                    return '{0} were {1}'
                else:
                    return '{0} was {1}'
            else:
                slf = 'You check yourself. You are ' + action['agent_name'] + "!\n"
                return slf + '{0} are {1}'

    def func(self, graph, args):
        room_id = graph.location(args[0])
        inv_text = graph.get_inventory_text_for(args[0])
        my_inv_action = {'caller': self.get_name(), 'name': 'list_inventory',
                         'room_id': room_id, 'actors': [args[0]],
                         'agent_name': graph.node_to_desc(args[0]),
                         'add_descs': [inv_text]}
        graph.send_action(args[0], my_inv_action)
        return True


class HealthFunction(SoloFunction):
    def __init__(self):
        super().__init__(
            function_name=['health', 'status'],
            callback_triggers=[
                {'action': 'check_health', 'args': [0]},
            ]
        )

    def get_action_observation_format(self, action, descs):
        if action['name'] == 'check_health':
            if descs[0] == 'You':
                return 'You checked your health. '
            elif descs[0] == 'I':
                return 'I checked my health. '
            else:
                return '{0} checked their health. '
        elif action['name'] == 'display_health':
            if 'past' in action:
                if descs[0] == 'You':
                    return '{0} were feeling {1}. '
                else:
                    return '{0} was feeling {1}. '
            else:
                if descs[0] == 'You':
                    return '{0} are feeling {1}. '
                else:
                    return '{0} is feeling {1}. '
        elif action['name'] == 'changed':
            return '{0} went from feeling {1} to feeling {2}. \n'
        return super().get_action_observation_format(action, descs)

    def func(self, graph, args):
        room_id = graph.location(args[0])
        health_text = graph.health(args[0])
        my_health_action = {'caller': self.get_name(),
                            'name': 'display_health',
                            'room_id': room_id, 'actors': [args[0]],
                            'add_descs': [health_text]}
        graph.send_action(args[0], my_health_action)
        return True


class LookFunction(SoloFunction):
    def __init__(self):
        super().__init__(
            function_name=['look', 'l'],
            callback_triggers=[
                {'action': 'looked', 'args': [0]},
            ]
        )
        self.formats = {'looked': '{0} looked around. '}

    def func(self, graph, args):
        room_id = graph.location(args[0])

        # Prepare and send action for listing room contents
        agent = graph.oo_graph.get_node(args[0])

        is_return = room_id in agent._visited_rooms
        if is_return or not graph.has_prop(room_id, 'first_desc'):
            room_desc = graph.get_prop(room_id, 'desc', None)
        else:
            room_desc = graph.get_prop(room_id, 'first_desc')
        agent._visited_rooms.add(room_id)
        if is_return or not graph.has_prop(room_id, 'first_desc'):
            agent_ids, agent_descs = \
                graph.get_nondescribed_room_agents(room_id)
            object_ids, object_descs = \
                graph.get_nondescribed_room_objects(room_id)
            _room_ids, room_descs = graph.get_room_edges(room_id)
        else:
            agent_ids, agent_descs = [], []
            object_ids, object_descs = [], []
            room_descs = []
        list_room_action = {
            'caller': self.get_name(), 'name': 'list_room', 'room_id': room_id,
            'actors': [args[0]], 'agent_ids': agent_ids,
            'present_agent_ids': agent_ids, 'object_ids': object_ids,
            'agent_descs': agent_descs, 'object_descs': object_descs,
            'room_descs': room_descs, 'room_desc': room_desc,
            'returned': False,
            'room_agents': graph.get_room_agents(room_id, drop_prefix=True),
        }
        graph.send_action(args[0], list_room_action)
        return True

    def format_observation(self, graph, viewing_agent, action,
                           telling_agent=None, is_constraint=False):
        '''Return the observation text to display for an action for the case
        of look. Look is a special case, as the description can change more
        than just tense based on who or what was seen and who you tell it to.
        '''
        if action['name'] != 'list_room':
            return super().format_observation(graph, viewing_agent, action,
                                              telling_agent, is_constraint)
        room_desc = action['room_desc']
        object_descs = action['object_descs']
        object_ids = action['object_ids']
        ents = {object_descs[i]: object_ids[i] for i in range(len(object_ids))}
        agent_descs = action['agent_descs'][:]
        agent_ids = action['agent_ids']
        room_descs = action['room_descs']
        room = action['room_id']
        actor_id = action['actors'][0]
        returned = action['returned']

        if telling_agent is None:
            # Override for first description to set it to EXACTLY what was
            # given.
            has_actors = len(agent_ids) > 0
            # TODO first looks are returning none!?
            # if not has_actors:
            #     return room_desc

            try:
                # Remove viewing agent from the list (it's implied)
                i = agent_ids.index(viewing_agent)
                del agent_descs[i]
            except BaseException:
                pass
            if returned:
                s = 'You are back '
            else:
                s = 'You are '
            s += 'in {}.\n'.format(graph.node_to_desc(room))
            if room_desc is not None:
                s += room_desc + '\n'
            if len(object_ids) > 0:
                s += graph.get_room_object_text(object_descs, ents)
            if len(agent_descs) > 0:
                s += graph.get_room_agent_text(agent_descs)
            if len(room_descs) > 0:
                s += graph.get_room_edge_text(room_descs)
            # handy helper to see if valid functions are working while in game,
            # commented for now, but handy to keep here.
            #s += 'Available actions:\n'
            #s += str(graph.get_available_actions_fast(actor_id))
            return s
        else:
            is_present = room == graph.location(actor_id)

            if telling_agent in agent_ids:
                # Remove telling agent from descriptions (its implied)
                i = agent_ids.index(telling_agent)
                del agent_descs[i]
                del agent_ids[i]
            if telling_agent in agent_ids:
                # Replace telling agent with I (I was there)
                i = agent_ids.index(telling_agent)
                if i < len(agent_descs):
                    agent_descs[i] = 'I'
            actor_desc = graph.node_to_desc(actor_id) + ' was'
            if actor_id == telling_agent:
                actor_desc = 'I am' if is_present else 'I was'
            elif actor_id == viewing_agent:
                actor_desc = 'You are' if is_present else 'You were'

            s = '{} in {}.\n'.format(actor_desc, graph.node_to_desc(room))
            if room_desc is not None:
                s += room_desc + '\n'
            s += graph.get_room_object_text(object_descs, ents,
                                            past=not is_present,
                                            give_empty=False)
            if viewing_agent in agent_ids:
                # Replace viewing agent with you were
                i = agent_ids.index(viewing_agent)
                del agent_descs[i]
                del agent_ids[i]
                s += 'You are here.\n' if is_present else 'You were there.\n'
            s += graph.get_room_agent_text(agent_descs, past=not is_present)
            s += graph.get_room_edge_text(room_descs, past=not is_present)
            return s


class UnfollowFunction(SoloFunction):
    def __init__(self):
        super().__init__(
            function_name=['unfollow'],
            callback_triggers=[
                {'action': 'stopped_following', 'args': [0]},
            ]
        )
        self.formats = {'unfollowed': '{0} stopped following {1}. ',
                        'failed': '{0} couldn\'t follow that. '}

    def func(self, graph, args):
        agent_id = args[0]
        room_id = graph.location(args[0])
        following = graph.get_following(agent_id)
        if following is None:
            graph.send_msg(agent_id, 'You are not following anyone.\n')
        else:
            graph.set_follow(agent_id, None)
            unfollow_action = {
                'caller': self.get_name(), 'name': 'unfollowed',
                'room_id': room_id, 'actors': [args[0], following],
            }
            graph.broadcast_to_room(unfollow_action)
        return True

func_list = [
    MoveAgentFunction(),
    GetObjectFunction(),
    PutObjectInFunction(),
    DropObjectFunction(),
    GiveObjectFunction(),
    StealObjectFunction(),
    WearObjectFunction(),
    WieldObjectFunction(),
    RemoveObjectFunction(),
    WaitFunction(),
    InventoryFunction(),
    HealthFunction(),
    EatFunction(),
    DrinkFunction(),
    LookFunction(),
    LockFunction(),
    UnlockFunction(),
    ExamineFunction(),
    FollowFunction(),
    UnfollowFunction(),
    HitFunction(),
    TellFunction(),
    HugFunction(),
    # UseFunction(),
    SayFunction(),
    WhisperFunction(),
    ShoutFunction(),
]
emotes = [
    'applaud', 'blush', 'cry', 'dance', 'frown', 'gasp', 'grin', 'groan',
    'growl', 'laugh', 'nod', 'nudge', 'ponder', 'pout', 'scream',
    'shrug', 'sigh', 'smile', 'stare', 'wave', 'wink', 'yawn'
]
for e in emotes:
    func_list.append(EmoteFunction(e))

# Construct list of graph functions by usable names
CANNONICAL_GRAPH_FUNCTIONS = {}
for f in func_list:
    names = f.name
    if type(names) is str:
        names = [names]
    for name in names:
        GRAPH_FUNCTIONS[name] = f
    CANNONICAL_GRAPH_FUNCTIONS[names[0]] = f

FUNC_IGNORE_LIST = ['tell', 'say', 'shout', 'whisper']
