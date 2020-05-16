#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai_internal.projects.light.v1.utils import get_article, get_node_view_or_self
from parlai_internal.projects.light.v1.graph_model.graph_nodes import (
    GraphRoom, GraphObject,
)


class GraphConstraint(object):
    '''
    Specific constraint to be made over the state of the graph, either as
    a prerequisite for an action occurring or as the requirement for a
    goal state to be validated.

    As a requirement they should implement two functions -
      is_satisfied(*args):
        returns a boolean for whether the given args satisfy
        the requirements of the contstraint.
      invalid_reason(*args):
        gives a best-effort reason for why the given arguments do not
        satisfy this constraint.
    '''

    NAME = 'GraphConstraint'

    def __init__(self, *args, **kwargs):
        '''
        Return a GraphConstraint that can be used to enforce a constraint
        on the graph.

        __init__ should set any required parts of generic constraints such
        that
        '''
        self.executed = False
        self.__setup_args = args
        self.__setup_kwargs = kwargs

    def is_satisfied(self, *args):
        '''
        This function can take in any args as specified by the function's
        description, and should return a boolean for whether the arguments
        over the graph satisfy the given constraints.
        '''
        raise NotImplementedError

    def invalid_reason(self, *args):
        '''
        This function should return best-guess in-game text for the reason
        for which the given action could not be accomplished.

        These should be considered a best guess, as GraphEvents have more
        context as to why something doesn't end up happeneing.
        '''
        raise NotImplementedError

    def __repr__(self):
        return f'{self.NAME}({self.__setup_args}, {self.__setup_kwargs})'


class FitsConstraint(GraphConstraint):
    '''Determining if one object will fit into another

    args are:
        0 => actor
        1 => object
        2 => container
    '''
    NAME = 'FitsConstraint'
    FIT_TYPES = ['carry', 'contain']

    def __init__(self, fit_type='contain'):
        assert fit_type in self.FIT_TYPES, f'Unexpected fit type {fit_type} provided'
        super().__init__(fit_type=fit_type)
        self.__fit_type = fit_type

    def is_satisfied(self, actor, graph_node, graph_container):
        '''
        This constraint is only satisfied if the given node fits in
        the given container
        '''
        return graph_container.would_fit(graph_node)

    def invalid_reason(self, actor, graph_node, graph_container):
        """
        There are a few cases for which this fails.
        If an object is really too massive and trying to be carried,
        it can't be lifted. Otherwise, it's just that there isn't enough space.
        """
        # Special handling for you cases
        node_is_you = actor == graph_node
        node_desc = get_node_view_or_self(actor, graph_node)
        container_desc = get_node_view_or_self(actor, graph_container)
        if self.__fit_type == 'carry':
            if graph_node.size >= 150:
                return f'{node_desc} isn\'t something you can pick up'.capitalize()
            else:
                return f'{container_desc} can\'t carry that much more.'.capitalize()
        else:
            if node_is_you:
                return "You don't fit."
            else:
                return f'{node_desc} does not fit.'.capitalize()


class IsTypeConstraint(GraphConstraint):
    '''
    Determining if an object has inherited all of a set of types.
    This is a generic constraint that should be initialized with specific
    classes and reasons.

    args are:
        0 => actor
        1 => target_node
    '''
    NAME = 'IsTypeConstraint'

    def __init__(self, expected_classes, failure_text=None):
        super().__init__(expected_classes=expected_classes, failure_text=failure_text)
        self.__expected_classes = expected_classes
        self.__failure_text = failure_text

    def _get_missing_classes(self, graph_node):
        return [x for x in self.__expected_classes if x not in graph_node.classes]

    def is_satisfied(self, actor, graph_node):
        '''
        This constraint is only satisfied if the given graph_node has all the
        expected classes
        '''
        return len(self._get_missing_classes(graph_node)) == 0

    def invalid_reason(self, actor, graph_node):
        """
        Explain that the given node was missing a particular class
        """
        assert not self.is_satisfied(actor, graph_node), (
            'Can not provide failure reason for satisfied constraint'
        )
        if self.__failure_text is not None:
            return self.__failure_text

        # TODO this grammar can be pretty bad in cases when classes are
        # attributes such as "burnable"
        missing_class = self._get_missing_classes(graph_node)[0]
        missing_class_txt = f'{get_article(missing_class)} {missing_class}'
        node_is_you = actor == graph_node
        node_desc = get_node_view_or_self(actor, graph_node)
        if node_is_you:
            return f'You are not {missing_class_txt}'
        return f'{node_desc} is not {missing_class_txt}'.capitalize()


class NotTypeConstraint(GraphConstraint):
    '''
    Determining if an object has not inherited a set of types.
    This is a generic constraint that should be initialized with specific
    classes and reasons.

    args are:
        0 => actor
        1 => target_node
    '''
    NAME = 'NotTypeConstraint'

    def __init__(self, rejected_classes, failure_text=None):
        super().__init__(rejected_classes=rejected_classes, failure_text=failure_text)
        self.__rejected_classes = rejected_classes
        self.__failure_text = failure_text

    def _get_rejected_classes(self, graph_node):
        return [x for x in self.__rejected_classes if x is graph_node.classes]

    def is_satisfied(self, actor, graph_node):
        '''
        This constraint is only satisfied if the given graph_node has all the
        expected classes
        '''
        return len(self._get_rejected_classes(graph_node)) == 0

    def invalid_reason(self, actor, graph_node):
        """
        Explain that the given node had an undesired class
        """
        assert not self.is_satisfied(actor, graph_node), (
            'Can not provide failure reason for satisfied constraint'
        )
        if self.__failure_text is not None:
            return self.__failure_text

        # TODO this grammar can be pretty bad in cases when classes are
        # attributes such as "burnable"
        rejected_class = self._get_rejected_classes(graph_node)[0]
        rejected_class_txt = f'{get_article(rejected_class)} {rejected_class}'
        node_is_you = actor == graph_node
        node_desc = get_node_view_or_self(actor, graph_node)
        if node_is_you:
            return f'You are {rejected_class_txt}'
        return f'{node_desc} is {rejected_class_txt}'.capitalize()


class HasPropConstraint(GraphConstraint):
    '''
    Determining if an object has a specific prop

    args are:
        0 => actor
        1 => graph_node
        2 => wanted_prop
    '''
    NAME = 'HasPropConstraint'

    def __init__(self, wanted_prop, failure_text=None):
        super().__init__(wanted_prop=wanted_prop, failure_text=failure_text)
        self.__wanted_prop = wanted_prop
        self.__failure_text = failure_text

    def is_satisfied(self, actor, graph_node):
        '''
        This constraint is only satisfied if the given graph_node has the
        wanted prop set by this constraint
        '''
        return graph_node.has_prop(self.__wanted_prop)

    def invalid_reason(self, actor, graph_node):
        """
        Explain that the given node was missing a particular prop
        """
        assert not self.is_satisfied(actor, graph_node), (
            'Can not provide failure reason for satisfied constraint'
        )
        if self.__failure_text is not None:
            return self.__failure_text

        # TODO this grammar can be pretty bad in cases when classes are
        # nouns such as "container"
        node_is_you = actor == graph_node
        node_desc = get_node_view_or_self(actor, graph_node)
        if node_is_you:
            return f'You are not {self.__wanted_prop}'
        return f'{node_desc} is not {self.__wanted_prop}'.capitalize()


class NoPropConstraint(GraphConstraint):
    '''
    Determining if an object has a specific prop

    args are:
        0 => actor
        1 => graph_node
        2 => bad_prop
    '''
    NAME = 'NoPropConstraint'

    def __init__(self, bad_prop, failure_text=None):
        super().__init__(bad_prop=bad_prop, failure_text=failure_text)
        self.__bad_prop = bad_prop
        self.__failure_text = failure_text

    def is_satisfied(self, actor, graph_node):
        '''
        This constraint is only satisfied if the given graph_node has the
        wanted prop set by this constraint
        '''
        return not graph_node.has_prop(self.__bad_prop)

    def invalid_reason(self, actor, graph_node):
        """
        Explain that the given node was had a blacklisted prop
        """
        assert not self.is_satisfied(actor, graph_node), (
            'Can not provide failure reason for satisfied constraint'
        )
        if self.__failure_text is not None:
            return self.__failure_text

        # TODO this grammar can be pretty bad in cases when classes are
        # nouns such as "container"
        node_is_you = actor == graph_node
        node_desc = get_node_view_or_self(actor, graph_node)
        if node_is_you:
            return f'You are {self.__bad_prop}'
        return f'{node_desc} is {self.__bad_prop}'.capitalize()


class LockableConstraint(GraphConstraint):
    '''Determining if a path can be locked

    args are:
        0 => actor
        1 => target
    '''
    NAME = 'LockableConstraint'

    def __init__(self, lockable=True, failure_text=None):
        super().__init__(lockable=lockable, failure_text=failure_text)
        self.__lockable = lockable
        self.__failure_text = failure_text

    def is_satisfied(self, actor, graph_node):
        '''
        This constraint is only satisfied if the given graph node or the
        connection between the actor's room and given graph nodes
        has the desired locking status
        '''
        if isinstance(graph_node, GraphRoom):
            # Locking an edge
            start_loc = actor.get_room()
            edge = start_loc.get_edge_to(graph_node)
            if edge is None:
                return False  # No such edge
            return self.__lockable == (edge.locked_edge is not None)
        elif isinstance(graph_node, GraphObject):
            # Locking a container
            return self.__lockable == (graph_node.get_prop('lockable', False))
        else:
            return False

    def invalid_reason(self, actor, graph_node):
        """
        Explain that the given node was missing a particular class
        """
        if self.__failure_text is not None:
            return self.__failure_text
        if actor == graph_node:
            return "You are not lockable."
        elif isinstance(graph_node, GraphRoom):
            # Locking an edge
            start_loc = actor.get_room()
            edge = start_loc.get_edge_to(graph_node)
            if edge is None:
                return "There's no path to lock from here to there."
            # As this constraint failed, if we wanted it lockable we should say
            # what we found wasn't lockable
            use_not = "not " if self.__lockable else ""
            return f"The path there is {use_not} lockable."
        elif isinstance(graph_node, GraphObject):
            # Locking a container
            use_not = "not " if self.__lockable else ""
            return f"{graph_node.get_prefix_view()} is {use_not} lockable.".capitalize()
        else:
            return f"There is no way to lock {graph_node.get_prefix_view()}."


class LockedConstraint(GraphConstraint):
    '''Determining if a path has a particular status

    args are:
        0 => actor
        1 => target
    '''
    NAME = 'LockedConstraint'

    def __init__(self, want_locked=True, failure_text=None):
        super().__init__(want_locked=want_locked, failure_text=failure_text)
        self.__want_locked = want_locked
        self.__failure_text = failure_text

    def is_satisfied(self, actor, graph_node):
        '''
        This constraint is only satisfied if the given graph node or the
        connection between the actor's room and given graph nodes
        has the desired locking status
        '''
        if isinstance(graph_node, GraphRoom):
            # Locking an edge
            start_loc = actor.get_room()
            edge = start_loc.get_edge_to(graph_node)
            if edge is None:
                return False  # No such edge
            if self.__want_locked == (edge.locked_edge is not None):
                return self.__want_locked is False  # isn't lockable, not locked
            return self.__want_locked == (edge.locked_edge.is_locked)
        elif isinstance(graph_node, GraphObject):
            # Locking a container
            # TODO make possible
            return self.__want_locked == (graph_node.get_prop('locked', False))
        else:
            return False

    def invalid_reason(self, actor, graph_node):
        """
        Explain that the given node was missing a particular class
        """
        if self.__failure_text is not None:
            return self.__failure_text
        if actor == graph_node:
            return "You are not lockable."
        elif isinstance(graph_node, GraphRoom):
            # Locking an edge
            start_loc = actor.get_room()
            edge = start_loc.get_edge_to(graph_node)
            if edge is None:
                return "There's no path to lock from here to there."
            if edge.locked_edge is None:
                return "That can't be locked"
            # As this constraint failed, if we wanted it lockable we should say
            # what we found wasn't lockable
            use_not = "not " if self.__want_locked else ""
            return f"The path there is {use_not} locked."
        elif isinstance(graph_node, GraphObject):
            # Locking a container
            use_not = "not " if self.__want_locked else ""
            return f"{graph_node.get_prefix_view()} is {use_not} locked.".capitalize()
        else:
            return f"There is no way to lock {graph_node.get_prefix_view()}."


class LockedWithConstraint(GraphConstraint):
    '''Determining if a path has a particular status

    args are:
        0 => actor
        1 => target
        2 => key
    '''
    NAME = 'LockedWithConstraint'

    def __init__(self, failure_text=None):
        super().__init__(failure_text=failure_text)
        self.__failure_text = failure_text

    def is_satisfied(self, actor, graph_node, key_node):
        '''
        This constraint is only satisfied if the given graph node or the
        connection between the actor's room and given graph nodes
        has the desired locking status
        '''
        if isinstance(graph_node, GraphRoom):
            # Locking an edge
            start_loc = actor.get_room()
            edge = start_loc.get_edge_to(graph_node)
            if edge is None:
                return False  # No such edge
            if edge.locked_edge is None:
                return False  # Not lockable, not locked with
            return edge.locked_edge.get() == key_node
        elif isinstance(graph_node, GraphObject):
            # Locking a container
            # TODO make possible
            raise NotImplementedError
        else:
            return False

    def invalid_reason(self, actor, graph_node, key_node):
        """
        Explain that the given node was missing a particular class
        """
        if self.__failure_text is not None:
            return self.__failure_text
        if actor == graph_node:
            return "You are not lockable."
        if isinstance(graph_node, GraphRoom):
            # Locking an edge
            start_loc = actor.get_room()
            edge = start_loc.get_edge_to(graph_node)
            if edge is None:
                return "There's no path to lock from here to there."
            if edge.locked_edge is None:
                return "That can't be locked"
            return f"{key_node.get_prefix_view()} doesn't lock {graph_node.get_view_from(start_loc)}".capitalize()
        elif isinstance(graph_node, GraphObject):
            # Locking a container
            # TODO make possible
            raise NotImplementedError
        else:
            return f"There is no way to lock {graph_node.get_prefix_view()}."


# TODO create constraint for is_in for goals
