# LIGHT Events

LIGHT `GraphEvent`s comprise all types of manipulations that can occur on a LIGHT `OOGraph`. These, on their own, include checks for parsing, valid construction and executability, etc, however construction of a `GraphEvent` alone doesn't actually manipulate the graph. Calling `GraphEvent.execute` on a LIGHT `World` is required to actually attempt the transition.

We use `GraphEvent`s to parse text commands into valid actions, find all possible valid events for a given model agent, replay previous logs, and more.


## Base Graph Events
The base events are `GraphEvent`, representing any action on the graph, `ErrorEvent`, which represents a failure to parse or execute an event, and `TriggeredEvent`, which represents an event that can only be created directly by another event, rather than being parsed out from a determined action.

The `GraphEvent` itself sets a baseline API for interacting with an `OOGraph` and making controllable transitions over it. This interface covers the direct and parsed creation of an event, as well as execution and failure conditions. Details are further expanded on in the `base.py` file and class definition, but the following gives a brief overview:
- `__init__`: Generally, `GraphEvent`s are boiled down to an interaction between nodes, but can also include arbitrary text (for directly messaging, or updating graph text state). As such, graphs require an `actor`, and then optionally have `target_nodes` which may be involved in the interaction, as well as `text_content` which can be any string used in the event.
- `execute`: Actually make direct changes to the `OOGraph`, or broadcast observable messages to agents in the `OOGraph`. At the moment, assumes that the event _can_ be successfully executed if it is properly constructed.
- `split_text_args`: Given a string, split into a list of possibly valid text lists to parse into arguments to form an event. Return an `ErrorEvent` if no such parsing is possible.
- `find_nodes_for_args`: Given a list of text args, find appropriate elements in the graph that both match the name and event requirements. Return an `ErrorEvent` if no such find is possible.
- `construct_from_args`: Use the given args returned from `find_nodes_for_args` to construct a `GraphEvent` of this type.
- `to_canonical_form`: Produces a standard text representation for the event, such that a `split_text_args -> find_nodes_for_args -> construct_from_args` pass would produce the same event.
- `get_valid_actions`: Return a list of `GraphEvent`s of this type that a given agent would be able to perform on the given graph, if any.
- `view_as`: Provides a string representation for the event from the perpsective of a given agent.

A complete list of instances of events is defined in `graph_events.py`.

## LIGHT Use Events

These event types cover the contents of `use_events.py`, `use_triggered_events.py`, and `constraint.py`. Overall these events describe any interaction of the type `use x with y`. Every use interaction (Described in the world as an `on_use` function) is made of two parts: `Constraints` and `Events`.

Note, the contents currently handled by the `magic.py` class should eventually be rolled into these types of events.

### `Constraint`s
`Constraints` are the conditions that must be fullfilled in order for an event to happen.

For example, if try to dig for a pirate treasure it will only trigger the `Find Treasure Chest` event if you use the shovel item in the spot with an X on it - if you try to use in another spot the event will not happen. Being in the X spot is a `Constraint` of the `Find Treasure Chest` event.

### `Event`s

`Events` describe the effects triggered from the ocurrence of an `Use Event`. For example, the aforementioned `Find Treasure Chest` use event would trigger a `Create Entity Event`, creating a `Treasure Chest` item inside the `X-spot landmark` object. These events are all of that `UseTriggeredEvent` type.

### `remaining_uses`

There's also a third element in the `UseEvent` called `remaining_uses`, which represent how many times this event can still be played out. For example, the event above should have `remaning_uses: 1` as it can only happen one time. If you try it another time, no treasure will be found. If the event can happen infinite times, you should use `remaining_uses: inf`.

### Formatting

Every constraint and event is a dictionary of the format:
```json
{
    "type": "...",
    "params": {
        ...
    }
}
```

Every `on_use` function is an array of Use events, which are arrays of `Constraints` and `Events` as described above. In general, when describing an object, the format of their custom interactions will be:

```json
"object_id": {
    "name": "object_name",
    "contain_size": 0,
    ...
    "on_use": [
        //Interaction 1
        {
            "events": {
                ...
            },
            "constraints": {
                ...
            },
            "remaining_uses": "..."
        },
        //Interaction 2
        {
            "events": {
                ...
            },
            "constraints": {
                ...
            },
            "remaining_uses": "..."
        },
        ...
    ]
}
```

## Constraint Types

### Is Holding

Checks whether the actor of the event is holding one of the objects involved in the event. The `complement` argument represent if the constraint is being applied on the item being used or the target of the `on_use` event. If you try to use a shovel in a muddy area, for example, to be holding the shovel. Is has the format:
```json
{
    "type": "is_holding",
    "params": {
        "complement": "used_item"
    }
}
```

### Used with Item
Checks whether the actor of the event is doing the event with a specific object. Certain events can only happen by using certain combinations of objects, so this is a must. It has the format:
```json
{
    "type": "used_with_item_name",
    "params": {
        "item": "muddy area"
    }
}
```

### Used with Agent
Checks if the target of the event is an agent. This is useful as some events modify attributes which only exist in agents, like for example, an `on_use` event which modifies the target's health. It uses no params. It has the format:
```json
{
    "type": "used_with_agent"
}
```

### In Room

Checks if the event is happening inside a specific room. Some events only happen in certain places, like a magic orb that only works when placed inside the sanctuary of its creator. It has the format:
```json
{
    "type": "in_room",
    "params": {
        "room_name": "Orc cave"
    }
}
```

### Attribute Compare Value
It compares the attribute of the Use event target with a list of possible values. The attribute to be compared is passed through `key` and the list of possible values is passed through the `list` argument. The comparison method is passed through `cmp_type`, which can be:
-  `eq` for equal or `==`
-  `neq`for not equal or `!=`
-  `greater` for greater or `>`
-  `geq` for greater than or equal, `>=`
-  `less`for less or `<`
-  `leq`for less than or equal, `<=`

It's important to remind that the attribute value needs to satisfy its comparison to only one of the list values, meaning this constraint's list works as an _OR_. In case of an _AND_ conjoint being necessary, use multiple `attribute_compare_value` constraints in the same Use event. It has the format:
```json
{
    "type": "attribute_compare_value",
    "params": {
        "type": "in_used_target_item",
        "key": "health",
        "list": "[0]",
        "cmp_type": "greater"
    }
}
```

## Event Types

### Create Entity
Creates an entity after the event happens. The entity created may belong to the room (In this case, `type = in_room`), the actor of the event (`type=in_actor`), the item being used on the Use event (`type=in_used_item`) or the target of the Use event itself (`type=in_use_target_item`). To use this event, it's necessary to specify where the entity is being created and the object itself. It has the format:

```json
{
    "type": "create_entity",
    "params": {
        "type": "in_used_target_item",
        "object": {
            "name_prefix": "an",
            "is_wearable": true,
            "name": "emerald ring",
            "desc": "A beautiful and mysterious ring.. could it have magical powers?"
        }
    }
}
```



### Broadcast Message
Broadcasts a message related to the Use event to the room the agent is currently in. To use it, it is necessary to specify the views of the message (Which message will be sent to the agent doing the use event, to agents in the same room, etc.). The format is as following:

```json
{
    "type": "broadcast_message",
    "params": {
        "self_view": "You say the words aloud, and runes on the scroll glow with gold.",
        "self_as_target_view": "You are struck with searing pain!",
        "self_not_target_view": "{recipient_text} is struck with searing pain!",
        "room_view": "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} is struck with searing pain!"
    }
}
```

#### Recipient Text and Actor Text templates
The templates used in the example (`{recipient_text}`and `{actor_text}`) refer to the target and actor of the Use event respectively - which are specified in the code by the name of the objects related to the event itself. For an use event of the format `use x with y`, `actor_text` refer to `x` and `recipient_text` refer to `y`. If necessary, you can use these two templates in strings for _any_ event, not only Broadcast Message events.


### Modify Attribute
This event modifies the value of a certain attribute involved in the Use event. The target (Which should have the attribute) and the attribute being modified are specified through the `type` and `key` fields. The `value` field specifies the numeric change in the attribute, its syntax is as follows:
-  `+num` means that `new_value = curr_value + num`
-  `-num` means that `new_value = curr_value - num`
-  `=num` means that `new_value = num`

And the general syntax for this event is:
```json
{
    "type": "modify_attribute",
    "params": {
        "type": "in_used_target_item",
        "key": "health",
        "value": "-20"
    }
}
```
