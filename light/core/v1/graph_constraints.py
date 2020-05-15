#!/usr/bin/env python3
import parlai_internal.projects.light.v1.callbacks as Callbacks
from parlai.utils.misc import Timer

from collections import Counter
from copy import deepcopy
import os
import random
from parlai_internal.projects.light.v1.graph_utils import format_observation

CONSTRAINTS = {}

# Constraints
class GraphConstraint(object):
    '''Stub class to define standard for graph constraints, implements shared
    code for executing them
    '''
    def format_observation(self, graph, viewing_agent, action,
                           telling_agent=None):
        return format_observation(self, graph, viewing_agent, action,
                                  telling_agent, is_constraint=True)

    def get_failure_action(self, graph, args, spec_fail='failed'):
        '''Given the args, return an action to represent the failure of
        meeting this constraint
        '''
        raise NotImplemented

    def get_action_observation_format(self, action, descs):
        '''Given the action, return text to be filled by the parsed args'''
        raise NotImplemented

    def evaluate_constraint(self, graph, args):
        '''Evaluates a constraint, returns true or false for if it is met'''
        raise NotImplemented


class FitsConstraint(GraphConstraint):
    '''Determining if one object will fit into another

    args are:
        0 => actor_id
        1 => object_id
        2 => container_id
    '''
    name = 'fits_in'

    def get_failure_action(self, graph, args, spec_fail='failed'):
        # Special case for being unable to lift room objects
        if graph.get_prop(args[1], 'size') >= 150:
            return {'caller': self.name, 'name': 'cant_lift',
                    'room_id': graph.location(args[0]),
                    'actors': args}
        return {'caller': self.name, 'name': spec_fail,
                'room_id': graph.location(args[0]),
                'actors': args}

    def get_action_observation_format(self, action, descs):
        if action['name'] == 'cant_carry':
            descs[2] = descs[2].capitalize()
            if 'past' in action:
                return '{2} couldn\'t carry that much more'
            return '{2} can\'t carry that much more. '
        if action['name'] == 'cant_lift':
            return '{1} isn\'t something you can pick up'
        if 'past' in action:
            return '{1} didn\'t fit. '
        elif descs[1] in ['You', 'I']:
            return '{1} do not fit. '
        else:
            return '{1} does not fit. '

    def evaluate_constraint(self, graph, args):
        '''Return true or false for whether the object would fit in the
        container
        '''
        return graph.obj_fits(args[1], args[2])


class IsTypeConstraint(GraphConstraint):
    '''Determining if an object has inherited a particular type'''
    name = 'is_type'

    def get_failure_action(self, graph, args, spec_fail='failed'):
        action = {'caller': self.name, 'name': spec_fail,
                  'room_id': graph.location(args[0]),
                  'actors': args[:2]}
        if len(args) == 4:
            action['add_descs'] = [args[3]]
        return action

    def get_action_observation_format(self, action, descs):
        if len(descs) == 3:
            return descs[2]
        if 'past' in action:
            return 'I couldn\'t find that. '
        else:
            return 'You couldn\'t find that. '

    def evaluate_constraint(self, graph, args):
        '''Return true or false for whether the object has any wanted class

        args are:
            0 => actor_id
            1 => found_id
            2 => expected_class/es
            3 => alternate failure text
        '''
        found_id = args[1]
        expected_classes = args[2]
        if type(expected_classes) is not list:
            expected_classes = [expected_classes]
        obj_classes = graph.get_prop(found_id, 'classes')
        for want_class in expected_classes:
            if want_class in obj_classes:
                return True
        return False


class NotTypeConstraint(GraphConstraint):
    '''Determining if an object has inherited a particular type'''
    name = 'not_type'

    def get_failure_action(self, graph, args, spec_fail='failed'):
        action = {'caller': self.name, 'name': spec_fail,
                  'room_id': graph.location(args[0]),
                  'actors': args[:2]}
        if len(args) == 4:
            action['add_descs'] = [args[3]]
        return action

    def get_action_observation_format(self, action, descs):
        if len(descs) == 3:
            return descs[2]
        if 'past' in action:
            return 'I couldn\'t find that. '
        else:
            return 'You couldn\'t find that. '

    def evaluate_constraint(self, graph, args):
        '''Return true or false for whether the object has any wanted class

        args are:
            0 => actor_id
            1 => found_id
            2 => expected_class/es
            3 => alternate failure text
        '''
        found_id = args[1]
        expected_classes = args[2]
        if type(expected_classes) is not list:
            expected_classes = [expected_classes]
        obj_classes = graph.get_prop(found_id, 'classes')
        for want_class in expected_classes:
            if want_class in obj_classes:
                return False
        return True


class HasPropConstraint(GraphConstraint):
    '''Determining if an object doesn't have a prop it should have'''
    name = 'has_prop'

    def get_failure_action(self, graph, args, spec_fail='failed'):
        return {'caller': self.name, 'name': spec_fail,
                'room_id': graph.location(args[0]),
                'actors': args[:2], 'add_descs': [args[2]]}

    spec_attribute_map = {
        'equipped': ['{1} had to be equipped first. ',
                     '{1} has to be equipped first. '],
    }

    def get_action_observation_format(self, action, descs):
        if 'past' in action:
            if descs[2] in self.spec_attribute_map:
                return self.spec_attribute_map[descs[2]][0]
            return '{1} wasn\'t {2}'
        else:
            if descs[2] in self.spec_attribute_map:
                return self.spec_attribute_map[descs[2]][1]
            return '{1} isn\'t {2}'

    def evaluate_constraint(self, graph, args):
        '''Return true or false for whether the object doesn't have a prop

        args are:
            0 => viewer
            1 => prop_id
            2 => bad_prop
        '''
        return graph.has_prop(args[1], args[2])


class NoPropConstraint(GraphConstraint):
    '''Determining if an object has a prop it shouldn't have'''
    name = 'no_prop'

    def get_failure_action(self, graph, args, spec_fail='failed'):
        return {'caller': self.name, 'name': spec_fail,
                'room_id': graph.location(args[0]),
                'actors': args[:2], 'add_descs': [args[2]]}

    spec_attribute_map = {
        'equipped': ['{1} had to be removed first. ',
                     '{1} has to be removed first. '],
    }

    def get_action_observation_format(self, action, descs):
        if 'past' in action:
            if descs[2] in self.spec_attribute_map:
                return self.spec_attribute_map[descs[2]][0]
            return '{1} was {2}'
        else:
            if descs[2] in self.spec_attribute_map:
                return self.spec_attribute_map[descs[2]][1]
            return '{1} is {2}'

    def evaluate_constraint(self, graph, args):
        '''Return true or false for whether the object doesn't have a prop

        args are:
            0 => viewer
            1 => prop_id
            2 => bad_prop
        '''
        return not graph.has_prop(args[1], args[2])


class LockableConstraint(GraphConstraint):
    '''Determining if a path has a particular status

    args are:
        0 => actor_id
        1 => target_id
        2 => should be lockable
    '''
    name = 'is_lockable'

    def get_failure_action(self, graph, args, spec_fail='failed'):
        return {'caller': self.name, 'name': spec_fail,
                'room_id': graph.location(args[0]),
                'actors': args[:2], 'add_descs': [args[2]]}

    def get_action_observation_format(self, action, descs):
        if descs[2]:  # Failed when it was supposed to be lockable
            return '{1} can\'t be locked! '
        else:
            return '{1} is lockable. '

    def evaluate_constraint(self, graph, args):
        '''Return true or false for whether the object would fit in the
        container
        '''
        actor_id, target_id, want_lockable = args[0], args[1], args[2]
        if 'room' in graph.get_prop(target_id, 'classes'):
            room_id = graph.location(actor_id)
            is_lockable = \
                graph.get_path_locked_with(room_id, target_id) is not None
        else:
            is_lockable = graph.get_prop(target_id, 'lockable', False)
        return want_lockable == is_lockable


class LockedConstraint(GraphConstraint):
    '''Determining if a path has a particular status

    args are:
        0 => actor_id
        1 => target_id
        2 => should be locked
    '''
    name = 'is_locked'

    def get_failure_action(self, graph, args, spec_fail='failed'):
        return {'caller': self.name, 'name': spec_fail,
                'room_id': graph.location(args[0]),
                'actors': args[:2], 'add_descs': [args[2]]}

    def get_action_observation_format(self, action, descs):
        if descs[2]:  # Failed when it was supposed to be locked
            return '{1} is unlocked. '
        else:
            return '{1} is locked. '

    def evaluate_constraint(self, graph, args):
        '''Return true or false for whether the object would fit in the
        container
        '''
        actor_id, target_id, want_locked = args[0], args[1], args[2]
        if 'room' in graph.get_prop(target_id, 'classes'):
            room_id = graph.location(actor_id)
            if room_id == target_id:
                return True
            is_locked = \
                graph.path_is_locked(room_id, target_id)
        else:
            is_locked = graph.get_prop(target_id, 'locked', False)
        return want_locked == is_locked


class LockedWithConstraint(GraphConstraint):
        '''Determining if a path has a particular status

        args are:
            0 => actor_id
            1 => target_id
            2 => key_id
        '''
        name = 'locked_with'

        def get_failure_action(self, graph, args, spec_fail='failed'):
            item_desc = graph.node_to_desc(args[2])
            return {'caller': self.name, 'name': spec_fail,
                    'room_id': graph.location(args[0]),
                    'actors': args[:2], 'add_descs': [item_desc]}

        def get_action_observation_format(self, action, descs):
            descs[2] = descs[2].capitalize()
            return '{2} doesn\'t work with that. '

        def evaluate_constraint(self, graph, args):
            '''Return true or false for whether the object would fit in the
            container
            '''
            actor_id, target_id, key_id = args[0], args[1], args[2]
            if 'room' in graph.get_prop(target_id, 'classes'):
                room_id = graph.location(actor_id)
                locked_with = \
                    graph.get_path_locked_with(room_id, target_id)
            else:
                locked_with = graph.get_prop(target_id, 'locked_with', False)
            return locked_with == key_id


class NotLocationOfConstraint(GraphConstraint):
    '''Ensuring a location isn't the same one as the actor

    args are:
        0 => actor_id
        1 => target_id
    '''
    name = 'not_location_of'

    def get_failure_action(self, graph, args, spec_fail='failed'):
        return {'caller': self.name, 'name': spec_fail,
                'room_id': graph.location(args[0]),
                'actors': args, 'add_descs': []}

    def get_action_observation_format(self, action, descs):
        return "You're already in that location. "

    def evaluate_constraint(self, graph, args):
        '''Return true or false for whether the object would fit in the
        container
        '''
        actor_id, target_id = args[0], args[1]
        return graph.location(actor_id) != target_id


con_list = [
    FitsConstraint(),
    IsTypeConstraint(),
    HasPropConstraint(),
    NoPropConstraint(),
    LockableConstraint(),
    LockedConstraint(),
    LockedWithConstraint(),
    NotLocationOfConstraint(),
    NotTypeConstraint(),
]

CONSTRAINTS = {c.name: c for c in con_list}
