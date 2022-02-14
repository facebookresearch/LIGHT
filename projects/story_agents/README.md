# Story Agents (working title) project stub

This folder contains code for the LIGHT Collaboration with GaTech. At the moment it only contains stubs that demonstrate how various parts of the codebase may be used.

# Simple world building script - build a world and then write to a file.

Usage:
```

```

# Simple interaction script - interact with a custom agent model in an interactive setting

Usage:
```

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
