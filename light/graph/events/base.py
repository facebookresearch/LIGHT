# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

#!/usr/bin/env python3

# Used for typehinting
from light.graph.elements.graph_nodes import (
    GraphAgent,
    GraphNode,
)
from light.world.utils.json_utils import (
    convert_dict_to_node,
    GraphEncoder,
    node_to_json,
)
from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
    Optional,
    Type,
    TYPE_CHECKING,
    Union,
)
import inspect
import json
from uuid import uuid4

if TYPE_CHECKING:
    from light.graph.structured_graph import OOGraph
    from light.world.world import World


def proper_caps(in_string: str) -> str:
    """Function for only capitalizing the very first letter without disturbing the rest"""
    # This implementation is O(n), so if string manipulation ends up being a long-term
    # problem for LIGHT we'll need to swap to ctypes to get this right
    return in_string[0].upper() + in_string[1:]


def proper_caps_wrapper(func):
    """Decorator to ensure output strings are properly capitalized (first letter)."""

    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is not None:
            try:
                result = proper_caps(result)
            except:
                print(f"Had difficulty with proper_caps on {result}")
        return result

    return wrap


class ProcessedArguments(NamedTuple):
    targets: List[GraphNode]
    text: Optional[str] = None


class GraphEvent(object):
    """
    Full singular storage of an event that occurs over the world. It stores
    all references to both execute the action over the world as well as
    to be used to reconstruct world states given a starting state and event
    set or to be able to provide agents in the world with the required context
    to know something happened.

    Events should implement all of the present within this class
    """

    # All invokable events should define at least one canonical name and
    # then many possible synonyms as possible.
    # Events that can only be triggered do not have to set anything.
    NAMES: List[str] = []

    def __init__(
        self,
        actor: GraphAgent,
        target_nodes: Optional[List[GraphNode]] = None,
        text_content: Optional[str] = None,
        event_id: Optional[str] = None,
    ):
        """
        Construct an event to be executed by the given actor on given nodes
        """
        if event_id is None:
            event_id = str(uuid4())
        self.executed: bool = False  # type: ignore
        self.actor = actor
        self.room = actor.get_room()
        self.target_nodes = [] if target_nodes is None else target_nodes
        if self.room is not False:
            self.present_agent_ids = [
                x.node_id for x in self.room.get_contents() if x.agent
            ]
            self._canonical_targets = [
                x.get_view_from(self.room) for x in self.target_nodes
            ]
        self.text_content = text_content
        self.event_id = event_id

    def execute(self, world: "World") -> List["GraphEvent"]:
        """
        Execute the current action on the given world. Return a list of
        additional events that are triggered from this one.
        """
        raise NotImplementedError

    def view_as(self, viewer: GraphAgent) -> Optional[str]:
        """Provide the way that the given actor should view this event"""
        raise NotImplementedError

    def to_canonical_form(self) -> Optional[str]:
        """
        Provide the text that this event's actor would use to invoke this event

        Return None if this event cannot be invoked and can only be triggered
        """
        return None

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], "ErrorEvent"]:
        """
        Try to extract all possible interpretations for the given text such that
        the returned list of arguments may be parsed into world nodes to
        instantiate an Event using.

        If no fully valid arguments can be parsed, it should make a best guess,
        and allow find_nodes_for_args to handle the error cases.

        Under a parsing error (bad formatting) it should return an ErrorEvent
        with any details to give to the actor.

        By default, returns the input text as a single argument as the only option.
        """
        return [[text]]

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, "ErrorEvent"]:
        """
        Given the text arguments returned by split_text_args, produce the
        arguments required for construct_from_args. Return an ErrorEvent if
        something goes wrong here.

        Default does no parsing and returns the given args
        """
        return ProcessedArguments(targets=[], text=" ".join(text_args))

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> Union["GraphEvent", "ErrorEvent"]:
        """
        Try to return an Event constructed from the given args, return
        ErrorEvent if there's a reason it can't be created.

        First argument will always be the actor, the rest are as defined in
        split_text_args
        """
        raise NotImplementedError

    @classmethod
    def get_valid_actions(
        cls, graph: "OOGraph", actor: GraphAgent
    ) -> List["GraphEvent"]:
        """
        Return any valid actions that can be taken by the given actor
        over the current graph. Default returns no events.
        """
        return []

    @staticmethod
    def from_json(input_json: str, world: "World") -> "GraphEvent":
        """
        Instantiate this event from the given json over the given world
        """
        attribute_dict = convert_dict_to_node(json.loads(input_json), world)
        class_ = GraphEvent
        if "__class__" in attribute_dict:
            class_name = attribute_dict.pop("__class__")
            module_name = attribute_dict.pop("__module__")
            # Must pass non empty list to get the exact module
            module = __import__(module_name, fromlist=[None])
            class_ = getattr(module, class_name)
            if "__failed_event" in attribute_dict:
                # Get the class type for the failed event (error)
                failed_module = __import__(
                    attribute_dict.pop("__error_module"), fromlist=[None]
                )
                attribute_dict["failed_event"] = getattr(
                    failed_module, attribute_dict["__failed_event"]
                )
                attribute_dict["failed_constraint"] = attribute_dict[
                    "__failed_constraint"
                ]

        arglist = [
            attribute_dict.pop(arg)
            for arg in inspect.getfullargspec(class_.__init__)[0]
            if arg != "self"
        ]
        event = class_(*arglist)
        for k, v in attribute_dict.items():
            event.__dict__[k] = v
        event.post_json_load(world)
        return event

    def post_json_load(self, world: "World") -> None:
        """Rectify any state following a load from json."""
        pass

    def to_json(self, viewer: GraphAgent = None, indent: int = None) -> str:
        """
        Convert the content of this action into a json format that can be
        imported back to the original with from_json
        """
        className = self.__class__.__name__
        use_dict = {k: v for k, v in self.__dict__.copy().items()}
        use_dict["viewer"] = viewer
        use_dict["__class__"] = className
        use_dict["__module__"] = self.__module__
        # TODO: Consider moving graph encoder to a utils since we use here too!
        res = json.dumps(use_dict, cls=GraphEncoder, sort_keys=True, indent=indent)
        return res

    def __repr__(self) -> str:
        args_str = f"{self.actor}"
        if len(self.target_nodes) > 0:
            args_str += f", {self.target_nodes}"
        if self.text_content is not None:
            args_str += f', "{self.text_content}"'
        return f"{self.__class__.__name__}({args_str})"

    def to_frontend_form(self, viewer: "GraphAgent") -> Dict[str, Any]:
        """
        Parse out the contents of this event as seen by the given agent
        and return a dict that is consumable by our frontends
        """
        contents = self.room.get_contents()
        present_dict = {x.node_id: x.name for x in contents if x.agent}
        present_objects_dict = {
            x.node_id: x.get_prefix_view() for x in contents if x.object
        }
        return {
            "text": self.view_as(viewer),
            "caller": self.__class__.__name__,
            "event_id": self.event_id,
            "target_nodes": [node_to_json(x) for x in self.target_nodes],
            "additional_text": self.text_content,
            "present_agent_ids": present_dict,
            "canonical_targets": self._canonical_targets,
            "room": node_to_json(self.room),
            "actor": node_to_json(self.actor),
            "objects": present_objects_dict,
        }


class ErrorEvent(GraphEvent):
    """
    Class to contain any failures of event parsing. These should not be
    executed, but should instead be used to convey the complete context
    of a failure to parse an action.
    """

    def __init__(
        self,
        failed_event: Type[GraphEvent],
        actor,
        display_text,
        target_nodes=None,
        failed_constraint=None,
    ):
        """
        Construct a representation of a failed event. This should have the
        targetted event type (such as SayEvent), the actor, the error text
        to display to the actor, and any other target nodes.

        It also can hold an optional failed constraint
        """
        super().__init__(actor, target_nodes)
        self.display_text = display_text
        self.__failed_event = failed_event
        self.__failed_constraint = failed_constraint
        self.entered_text = None

    def set_entered_text(self, entered_text):
        """Set the text tentered for this event to be loaded later"""
        self.entered_text = entered_text

    def execute(self):
        """
        ErrorEvents represent failed actions (by parsing or constraint
        invalidation), and are thus not executable
        """
        raise Exception("ErrorEvents should never be executed")

    @proper_caps_wrapper
    def view_as(self, actor):
        """ErrorEvents should be viewed by the actor who tried to act"""
        assert actor == self.actor, (
            "ErrorEvents should only be viewed by the actor who tried to "
            "invoke an action."
        )
        return self.display_text

    def __repr__(self):
        return f"ErrorEvent({self.display_text}, {self.target_nodes})"

    # Error event overrides, needs __failed_event for constructor
    def to_json(self, viewer: GraphAgent = None, indent: int = None) -> str:
        """
        Convert the content of this action into a json format that can be
        imported back to the original with from_json
        """
        className = self.__class__.__name__
        use_dict = {
            k: v
            for k, v in self.__dict__.copy().items()
            if not k.startswith(f"_{className}__")
        }
        use_dict["__failed_event"] = self.__failed_event.__name__
        use_dict["__error_module"] = self.__failed_event.__module__
        use_dict["__failed_constraint"] = self.__failed_constraint

        use_dict["viewer"] = viewer
        use_dict["__class__"] = className
        use_dict["__module__"] = self.__module__
        # TODO: Consider moving graph encoder to a utils since we use here too!
        res = json.dumps(use_dict, cls=GraphEncoder, sort_keys=True, indent=indent)
        return res


class TriggeredEvent(GraphEvent):
    """
    Graph events that cannot be invoked, but are instead triggered during the
    execution of other events.
    """

    @classmethod
    def split_text_args(
        cls, actor: GraphAgent, text: str
    ) -> Union[List[List[str]], "ErrorEvent"]:
        """Triggered events are never parsed, and shouldn't call this"""
        raise Exception("Triggered events are never parsed")

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """Triggered events are never parsed, and shouldn't call this"""
        raise Exception("Triggered events are never parsed")

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> GraphEvent:
        """Triggered events are never parsed, and shouldn't call this"""
        raise Exception("Triggered events are never parsed")

    def to_cannonical_form(self) -> str:
        """Triggered events are never parsed, and shouldn't call this"""
        raise Exception("Triggered events are never parsed")


class NoArgumentEvent(GraphEvent):
    """Base class for GraphEvents that don't require any additional arguments"""

    @classmethod
    def split_text_args(cls, actor: GraphAgent, text: str) -> List[List[str]]:
        """No argument functions shouldn't have any text, but we can just ignore"""
        return [[]]

    @classmethod
    def find_nodes_for_args(
        cls, graph: "OOGraph", actor: GraphAgent, *text_args: str
    ) -> Union[ProcessedArguments, ErrorEvent]:
        """No argument functions don't have any arguments to find"""
        return ProcessedArguments(targets=[], text=None)

    @classmethod
    def construct_from_args(
        cls,
        actor: GraphAgent,
        targets: List["GraphNode"],
        text: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> GraphEvent:
        """No argument events can always be constructed from just the actor"""
        return cls(actor)

    @classmethod
    def get_valid_actions(
        cls, graph: "OOGraph", actor: GraphAgent
    ) -> List["GraphEvent"]:
        """No argument events can always be constructed from just the actor"""
        return [cls(actor)]

    def to_canonical_form(self) -> str:
        """No argument functions are just the name of the function"""
        return self.NAMES[0]
