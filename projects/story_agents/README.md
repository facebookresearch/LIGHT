# Story Agents (working title) project stub

This folder contains code for the LIGHT Collaboration with GaTech. At the moment it only contains stubs that demonstrate how various parts of the codebase may be used.

# Simple world building script - build a world and then write to a file.
The `create_map.py` file is an example of creating a LIGHT world using a graph builder. It relies on the example builder in `example_builder.py` to demonstrate the semantics of an example builder. Here, the `--use-simple` flag just relies on the `LIGHTDatabase` to provide random elements, and creates a simple assortment with two rooms and one character. `--map-file` is an argument for the filename in `outputs` to use.

Usage:
```
>> python create_map.py --use-simple
[loading db...]
[loading builder model...]
[Building light graph]
Warning - no magic file at /scratch/light/data/magic.db, skipping!
[ loaded 0 magic items]
[Writing out file to outputs/map.json]
```

# Simple interaction script - interact with a custom agent model in an interactive setting
The `play_map.py` file is a simple example of constructing an event loop using an `OOGraph` and `World` (constructed by the `GraphBuilder` above, for instance), and filling it with a `Soul` that allows for interacting in the world. `--map-file` is an argument to select which map in `outputs` to use.

Usage:
```
>> python play_map.py
[loading db...]
[loading map...]
Warning - no magic file at /scratch/light/data/magic.db, skipping!
[ loaded 0 magic items]
GraphAgent(bat king_1) enter act> look
I, GraphAgent(bat king_1), observed an event! LookEvent(GraphAgent(bat king_1))
In this function, I can react to it however I want
I could even trigger a `self.world.parse_exec` if I wanted to
Full event text:  You are in the Personal rooms.
There is a comfortable, but not ornate bed against the wall in the center of the room. There is a dresser and a mirror against the opposite wall. There are various paintings hung throughout the room of landscapes and past kings and queens. There is a fireplace on the east wall with a bearskin rug on the floor in front of it, and two chairs to sit in.
There's a fin poking up from the water here.
There's a path over there.

GraphAgent(bat king_1) enter act> get fin
I, GraphAgent(bat king_1), observed an event! GetObjectEvent(GraphAgent(bat king_1), [GraphObject(fin poking up from the water_2), GraphRoom(personal rooms_0)])
In this function, I can react to it however I want
I could even trigger a `self.world.parse_exec` if I wanted to
Full event text:  You got a fin poking up from the water.
GraphAgent(bat king_1) enter act> inv
I, GraphAgent(bat king_1), observed an event! InventoryEvent(GraphAgent(bat king_1))
In this function, I can react to it however I want
I could even trigger a `self.world.parse_exec` if I wanted to
Full event text:  You check yourself. You are a bat king!
You are carrying a fin poking up from the water.

GraphAgent(bat king_1) enter act> go over there
I, GraphAgent(bat king_1), observed an event! LeaveEvent(GraphAgent(bat king_1), [GraphRoom(inside tower_3)])
In this function, I can react to it however I want
I could even trigger a `self.world.parse_exec` if I wanted to
Full event text:  None
I, GraphAgent(bat king_1), observed an event! ArriveEvent(GraphAgent(bat king_1), "arrived from a path aways over")
In this function, I can react to it however I want
I could even trigger a `self.world.parse_exec` if I wanted to
Full event text:  None
I, GraphAgent(bat king_1), observed an event! LookEvent(GraphAgent(bat king_1))
In this function, I can react to it however I want
I could even trigger a `self.world.parse_exec` if I wanted to
Full event text:  You are in the Inside Tower.
The walls and are made of marble and trimmed in gold.  So too are the winding stairs that lead up to the observation deck.  Ivy lines the outside of the walls and sprawls all the way up the side to just near the top of the tower.  The tower itself is intimidating for those who dare to approach.  The tower stands tall so as to see out way across the beautiful land it watches over.
There's a path aways over.

GraphAgent(bat king_1) enter act>
```

# Replaying existing quests

From here, it would likely be relevant to use some of our existing datasets to accomplish next steps. The `light:quest_wild_completions` dataset contains all of the human-completed quest step episodes. The builder file [here](https://github.com/facebookresearch/LIGHT/blob/main/light/modeling/tasks/quests/wild_chats/build.py) pulls the raw data and creates episodes of the following type:
```
- - - NEW EPISODE: light:quest_wild_completions - - -
_setting_name Horse Tent
_setting_desc Held erect by large bronze poles planted firmly in the ground, the purple and gold Horse tent offers a canvas over a number of stalls, each with it's own accommodations including fresh hay and a trough that is refilled daily. The tent's entrance is kept open during the day to allow sunlight to shine into the tent illuminating those inside, while the other end of the tent has a door leading directly into the guest castle.
_partner_name horse
_self_name squire
_self_persona I am the King's Squire form the Eastern lands. I was taken from my family when I was just eight years old. I spend my days waiting for my moment to runaway.
_partner_persona I am a big strong beast. I help with pulling heavy items. I am great transportation and can be ridden by man and tied to a wagon to carry more people.
_self_motivation I want to use the ritual knife to release the horse
_partner_motivation
_partner_say I am but a small animal, I can't carry you, only myself.
_self_say Yes, but you are the kings prized horse. They will cause commotion trying to catch you, then I shall flee freely
_partner_say What is in it for me? There will be no riding on anyone's back!
_self_act wield ritual knife
_partner_say I shall free you
_self_say You aren't the only one with a blade!
_partner_say Who else does?
_self_say If you've come to kill me, you are not the first and you will not be the last.
_partner_say No you stupid horse, I want your freedom
_self_say I will free you into the wild. I am tired of the king and so are you by the looks of it.
_partner_act hug horse

   We understand each other now

```
These have previous turns from the player attempting to copmlete the `_self_motivation`'s target goal. More direct content is in the raw files downloaded by the build.

# Creating new interactions: an overview

Ultimately, for simple episodes, it'll likely involve creating rooms with one "rl agent" and zero or more "environment agents". Env agents can use any of our existing `Soul`s, while the RL agent will likely follow some base class you work on here. You can use the `World` to construct a simple RL loop, similar to the interactive scripts.
