


# LIGHT Events

  

An event is any interaction triggered or not by player action between two entities in the LIGHT environment.

  

## LIGHT Use Events

  

These events describe any interaction of the type `use x with y`. Every use interaction (Described in the world as an `on_use` function) is made of two parts:

`Constraints` and `Events`. `Constraints` are the conditions that must be fullfilled in order for an event to happen. For example, if try to dig for a pirate treasure

it will only trigger the `Find Treasure Chest` event if you use the shovel item in the spot with an X on it - if you try to use in another spot the event will not happen.

Being in the X spot is a `Constraint` of the `Find Treasure Chest` event.

`Events` describe the effects triggered from the ocurrence of an `Use Event`. For example, the aforementioned `Find Treasure Chest` use event would trigger a `Create Entity Event`, creating a `Treasure Chest` item inside the `X-spot landmark` object.

Every constraint and event is a dictionary of the format:
```
{
	"type": "...",
	"params": {
		...
	}
}
```

Every `on_use` functions is an array of Use events, which are arrays of `Constraints` and `Events` as described above. In general, when describing an object, the format of their custom interactions will be:
```
"object_id": {
	"name": "object_name",
	"contain_size": 0,
	...
	"on_use": [
		//Event 1
		{
			"events": {
				...
			},
			"constraints": {
				...
			}
		},
		//Event 2
		{
			"events": {
				...
			},
			"constraints": {
				...
			}
		},
		...
	]
}

```

## Constraint Types

### Is Holding

Checks whether the actor of the event is holding one of the objects involved in the event. The `complement` argument represent if the constraint is being applied on the item being used or the target of the `on_use` event. If you try to use a shovel in a muddy area, for example, to be holding the shovel. Is has the format:
```
{
	"type": "is_holding",
	"params": {
		"complement": "used_item"
	}
}
```

### Used with Item

Checks whether the actor of the event is doing the event with a specific object. Certain events can only happen by using certain combinations of objects, so this is a must. It has the format:
```
{
	"type": "used_with_item_name",
    "params": {
        "item": "muddy area"
    }
}
```
### Used with Agent

Checks if the target of the event is an agent. This is useful as some events modify attributes which only exist in agents, like for example, an `on_use` event which modifies the target's health. It uses no params. It has the format:
```
{
	"type": "used_with_agent"
}
```
### In Room

Checks if the event is happening inside a specific room. Some events only happen in certain places, like a magic orb that only works when placed inside the sanctuary of its creator. It has the format:
```
{
	"type": "in_room",
	"params": {
		"room_name": "Orc cave"
	}
}
```
### Attribute Compare Value

It compares the attribute of the Use event target with a list of possible values. The attribute to be compared is passed through `key` and the list of possible values is passed through the `list`  argument. The comparison method is passed through `cmp_type`, which can be:

- `eq` for equal or `==`
- `neq`for not equal or `!=`
- `greater` for greater or `>`
- `geq` for greater than or equal, `>=`
- `less`for less or `<`
- `leq`for less than or equal, `<=`

It's important to remind that the attribute value needs to satisfy its comparison to only one of the list values, meaning this constraint's list works as an _OR_. In case of an _AND_ conjoint being necessary, use multiple `attribute_compare_value` constraints in the same Use event. It has the format:
```
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
```
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
```

### Broadcast Message

Broadcasts a message related to the Use event to the room the agent is currently in. To use it, it is necessary to specify the views of the message (Which message will be sent to the agent doing the use event, to agents in the same room, etc.). The format is as following:
```
"type": "broadcast_message",
"params": {
	"self_view": "You say the words aloud, and runes on the scroll glow with gold.",
	"self_as_target_view": "You are struck with searing pain!",
	"self_not_target_view": "{recipient_text} is struck with searing pain!",
	"room_view": "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} is struck with searing pain!"
}
```

#### Recipient Text and Actor Text templates

The templates used in the example (`{recipient_text}`and `{actor_text}`) refer to the target and actor of the Use event respectively - which are specified in the code by the name of the objects related to the event itself. For an use event of the format `use x with y`, `actor_text` refer to `x` and `recipient_text` refer to `y`. If necessary, you can use these two templates in strings for _any_ event, not only Broadcast Message events.


### Modify Attribute

This event modifies the value of a certain attribute involved in the Use event. The target (Which should have the attribute) and the attribute being modified are specified through the `type` and `key` fields. The `value` field specifies the numeric change in the attribute, its syntax is as follows:

- `+num` means that `new_value = curr_value + num`
- `-num` means that `new_value = curr_value - num`
- `=num` means that `new_value = num`

And the general syntax for this event is:
```
{
	"type": "modify_attribute",
	"params": {
		"type": "in_used_target_item",
		"key": "health",
		"value": "-20"
	}
}
```
