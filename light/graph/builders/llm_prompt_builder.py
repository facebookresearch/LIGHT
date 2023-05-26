"""
Currently contains the prompts used to create a builder that
constructs a full world from just a text prompt
by using a series of queries against a large language model
"""

import time
import openai
import random
from light.graph.builders.base import (
    GraphBuilder,
    GraphBuilderConfig,
    SingleSuggestionGraphBuilder,
    POSSIBLE_NEW_ENTRANCES,
)
from light.graph.structured_graph import OOGraph
from light.world.world import World, WorldConfig

from functools import wraps
from omegaconf import MISSING, DictConfig
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import (
        GraphRoom,
        GraphNode,
        NodeProps,
        GraphAgent,
    )

# We can go from a vague description of a setting (later called the prompt) to some possible seed locations
PROMPT_TO_LOCATIONS = """
Given a prompt for a medieval fantasy story, provide a list of {} major locations relevant to telling the story. For example, "A town overtaken by fear from the dragon that settled nearby" may include locations like: dragon's cave, town square, local inn, blacksmith's shop, forest near the dragon cave, etc.

Prompt: {}
Locations:
1."""  # sample prompt: The dwarven stronghold, set inside a dormant volcano with wolf-infested forests.

# This query can take the overall prompt and try to give characters for the story
PROMPT_TO_CHARACTERS = """Given a prompt for a medieval fantasy story setting, provide a list of {} major characters relevant to telling the story. For example, "A town overtaken by fear from the dragon that settled nearby" may include characters like: dragon, townsfolk, blacksmith, knight, etc. The characters should be mostly related to the prompt.

Prompt: {}
Characters:
1."""

# Generally, we should only develop the full description for contents that are of the self-contained category
LOCATION_TO_CATEGORY = """Given a location, determine which of the following labels are most appropriate:
self-contained: A singular setting that is small enough to be considered a set for a single shot in a movie. One example is "Blacksmith's counter".
generic: A generic grouping of locations or large generic location that one can provide a single instance for. One example is "Castle towers".
composite: A large location that would require multiple sub-sections for individual scenes. One example is "Town Center".
not a location: For entry that isn't a valid room or setting. One example is "Spoon".

Location: graveyard
Category: self-contained

Location: river
Category: generic

Location: Nearby Town
Category: composite

Location: Old Sunglasses
Category: not a location

Location: town gates:
Category: self-contained

Location: facilities on the border
Category: generic

Location: {}
Category:"""

# This query can split up composite locations into ideally some sub-sections
COMPOSITE_TO_COMPONENTS = """Given a large setting, provide a list of up to 6 location names that may be relevant to telling a fantasy story inside of that setting. One example is provided

Setting: Nearby Town
1. Central well
2. Blacksmith's shop
3. Town tavern
4. School
5. Graveyard
6. Marketplace

Note the overall context for this story when coming up with contained elements: {}

Setting: {}
1."""

# This query can move a grouping to a specific instance
GROUPING_TO_INSTANCES = """Given a generic location name in a fantasy adventure, provide one to three specific instances of that location. Two examples are given below:

Setting: Far-off land that is known for culinary delicacies
Location: stores
1. spice shop
2. butcher

Setting: Outpost of the kingdom, where the king's defenses reside.
Location: barracks
1. knight's bedroom
2. armor storage

Setting: {}
Location: {}
1."""

# This query should produce a Description and Backstory for the given location name.
LOCATION_NAME_TO_DESCRIPTIONS = """Given a location name and the setting of a medieval fantasy story it is supposed to appear in, provide both a text-adventure-style description and backstory in third-person perspective. The description should include characters and objects that may be found inside, narrated as if the person is reporting what it looks like when present there. The backstory should be flavor text about how the location came to be. One example is below.

Setting: The dwarven stronghold, set inside a dormant volcano with wolf-infested forests.
Location: The clearing where the sentries stand watch
Description: A small clearing near the entrance to the dwarven stronghold. Two sentries stand watch here, armed with axes and shields. There's a small campsite set up near the entrance, with a few barrels and crates stacked nearby. A few crows are perched on the barrels, cawing softly. Nearby is a small dark tunnel leading into the heart of the mountain. It looks like it would be a tight squeeze for anyone larger than a dwarf.
Backstory: The clearing in the forest existed long before the dwarves, but they've turned it into an outpost of sorts, watching for any potential threats to the stronghold. It would be a useful hunting ground as well, but the dwarves are more interested in smithing than hunting.

Setting: {}
Location: {}
Description:"""

# This query can take a room description and produce the labelling of characters, locations, and objects
LOCATION_ANNOTATION = """Given a setting, location name, description, and backstory, label the characters, objects currently present within the location according to the description. Also note nearby locations that are referenced in the description. If none in a category, write "- None"

Setting: A town overtaken by fear from the dragon that settled nearby
Location name: Town center
Description: The town center is a busy place, even with the fear of the dragon lurking nearby. The market stalls are full of people haggling for prices, and the bakery is doing a brisk business. The tavern is full of people trying to forget their troubles with ale. In the center of the square is a statue of the town's founder, looking stern and imposing.
Characters:
- townsfolk
Objects:
- statue of the town's founder
Nearby Locations:
- Market
- Bakery
- Tavern

Setting: {}
Location name: {}
Description: {}
Characters:"""

# This query can take the prompt and a character and produce a relevant persona, description, and motivation
PROMPTED_CHARACTER_ANNOTATION = """Given a medieval fantasy story setting and a character name, provide the following details for the singular form of the character. Follow the provided template:
Setting: The setting to use as context
Character Name: The name of the character to provide
Singular Form: the singular form of the provided character
Plural Form: a plural form for the provided character
Singular Persona: A first-person set of defining goal, characteristics, or backstory for this singular character
Singular Physical Description: An appropriate physical description for the character in third person, such that it could be used in narration to someone not present.
Singular Motivation: A single goal relevant to what this character wants to achieve
Emoji: the most relevant emoji representing this character or their persona

For example:
Setting: The dwarven stronghold, set inside a dormant volcano with wolf-infested forests.
Character Name: chief of the dwarves
Singular Form: cheif of the dwarves
Plural Form: cheifs of the dwarves
Singular Persona: I lead over all of the dwarves in the stronghold. Keeping them safe is my priority, though I fear that the wolves are becoming a threat. I try to be kind and gracious.
Singular Physical Description: This dwarf may be small in stature, but they carry themselves as a true leader.
Singular Motivation: Gather information about possible threats to the stronghold.
Emoji: ⛏

Setting: {}
Character Name: {}
Singular Form:"""

# This query can take a character and their relevant location and produce a relevant persona, description, and motivation, with wearing/wielding/carrying
ROOM_CHARACTER_ANNOTATION = """Given a medieval fantasy story setting description and a character name, provide the following details for the singular form of the character. Follow the provided template:
Setting: The setting to use as context
Character Name: The name of the character to provide
Singular Form: the singular form of the provided character
Plural Form: a plural form for the provided character
Singular Persona: A first-person set of defining goal, characteristics, or backstory for this character
Singular Physical Description: An appropriate physical description for the character in third person, such that it could be used in narration to someone not present.
Singular Motivation: A single goal relevant to what this character wants to achieve
Emoji: the most relevant emoji representing this character or their persona
Carrying: List of objects carried
Wielding: List of objects wielded
Wearing: List of objects worn

For example:
Setting: A small clearing near the entrance to the dwarven stronghold. Two sentries stand watch here, armed with axes and shields. There's a small campsite set up near the entrance, with a few barrels and crates stacked nearby. A few crows are perched on the barrels, cawing softly. Nearby is a small dark tunnel leading into the heart of the mountain. It looks like it would be a tight squeeze for anyone larger than a dwarf.
Backstory: The clearing in the forest existed long before the dwarves, but they've turned it into an outpost of sorts, watching for any potential threats to the stronghold. It would be a useful hunting ground as well, but the dwarves are more interested in smithing than hunting.
Character Name: Sentry
Singular Form: Sentry
Plural Form: Sentries
Singular Persona: I keep watch over the stronghold. I try to be kind and gracious. If a threat presents itself though, I'll have no mercy.
Singular Physical Description: This dwarf seems strong and nimble. They probably know their way around a weapon.
Singular Motivation: Keep the stronghold safe.
Emoji: ⚔
Carrying:
- None
Wielding:
- Axe
- Shield
Wearing:
- Helmet
- Armor

Setting: {}
Character Name: {}
Singular Form:"""

# This query can take an object and their relevant character and provide a description and attributes
OBJECT_ANNOTATION = """Given a an object name from a medieval fantasy text adventure, provide a physical description for the singular form, as well as values for the specific attributes below. Include an appropriate paranthetical article for names. For example:
Name: swords
Singular form: sword
Plural form: swords
Singular description: This sword is sharp and heavy, and could likely do a lot of damage if swung. Don't swing it at anything important!
Food: no
Drink: no
Holdable: yes
Wearable: no
Wieldable: yes
Surface: no
Container: no

Name:{}
Singular form:"""

# This query can take a list of rooms and provide the 5 most likely neighbors for each room
ROOM_NEIGHBORS = """You are given a list of locations in a fantasy text adventure story. Imagine you were arranging them into a map. For each location in the list provide the at most 5 other locations in the list likely to appear nearby in a map. Format the response as "Location : comma separated nearby locations"

Locations:
{}
Neighbor Lists:
1."""

# This query can take the original state of the room and try to adapt to a new setting
ROOM_TO_ROOM = """You will be given a setting description and the list of characters and objects expected to be present for that description. You will also be given a list of new characters and objects that are present. Adapt the description to fit the changes provided. One example below:

Setting: A town overtaken by fear from the dragon that settled nearby
Location name: Town center
Description: The town center is a busy place, even with the fear of the dragon lurking nearby. The market stalls are full of people haggling for prices, and the bakery is doing a brisk business. The tavern is full of people trying to forget their troubles with ale. In the center of the square is a statue of the town's founder, looking stern and imposing.
Listed locations:
- market
- bakery
- tavern
Original Characters:
- townsfolk
Original Objects:
- statue of the town's founder
Changes:
- remove townsfolk
- add milkman
New Description: The town center is usually a busy place, but with the fear of the dragon lurking nearby only a milkman is out right now. The nearby market stalls and baker are mostly empty. Perhaps people are hiding in the tavern? In the center of the square is a statue of the town's founder, looking stern and imposing.

Setting: {}
Location name: {}
Description: {}
Listed locations:
{}
Original Characters:
{}
Original Objects:
{}
Changes:
{}
New Description:"""


@dataclass
class LLMPromptBuilderConfig(GraphBuilderConfig):
    prompt: str = field(
        default="",
        metadata={"help": ("Description string to prompt the pipeline with")},
    )
    num_rooms: float = field(
        default=20,
        metadata={"help": ("Number of rooms to stitch together")},
    )
    num_characters: bool = field(
        default=15,
        metadata={"help": ("cap on number of characters to include")},
    )


@dataclass
class GPT3LLMBuilderConfig(LLMPromptBuilderConfig):
    _backend: str = "openai"
    openai_org_id: str = field(
        default=MISSING,
        metadata={"help": ("Org ID for OpenAI API")},
    )
    openai_secret_key: str = field(
        default=MISSING,
        metadata={"help": ("Secret Key for OpenAI API")},
    )


last_query_time = time.time()
last_query = None


def query_openai(
    prompt: str,
    temperature: float = 0.7,
    top_p: float = 1.0,
    frequency_penalty: float = 0,
    presence_penalty: float = 0,
):
    """Wrapper around openai queries, with some parameters"""
    global last_query
    completion = openai.Completion.create(
        engine="text-davinci-002",
        temperature=temperature,
        top_p=top_p,
        prompt=prompt,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_tokens=700,
    )
    last_query = f"Prompt: {prompt}\nGeneration: {completion.choices[0].text.strip()}"
    print(".", end="", flush=True)
    return completion.choices[0].text.strip()


def retry(count=5, exc_type=Exception):
    def decorator(func):
        @wraps(func)
        def result(*args, **kwargs):
            ret_exec = "No Query"
            for _i in range(count):
                try:
                    return func(*args, **kwargs)
                except exc_type as e:
                    ret_exec = e
                    print("e", end="", flush=True)
            print("Exception Query:\n" + last_query)
            raise ret_exec

        return result

    return decorator


@retry(count=8)
def get_story_locations(
    story_prompt: str, builder_config: "DictConfig", num_locs: int = 10
) -> List[str]:
    """Get a list of story locations given a related story prompt"""
    final_prompt = PROMPT_TO_LOCATIONS.format(num_locs, story_prompt)
    if builder_config._backend == "openai":
        result = query_openai(
            final_prompt,
            frequency_penalty=0.15,
            presence_penalty=0.1,
        )
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = "1. " + result
    lines = result.split("\n")
    locations = [l.split(". ", 1)[1].strip() for l in lines]
    return locations


@retry(count=8)
def get_story_characters(
    story_prompt: str, builder_config: "DictConfig", num_chars: int = 10
) -> List[str]:
    """Get a list of story characters given a related story prompt"""
    final_prompt = PROMPT_TO_CHARACTERS.format(num_chars, story_prompt)
    if builder_config._backend == "openai":
        result = query_openai(
            final_prompt,
            frequency_penalty=0.15,
            presence_penalty=0.1,
        )
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = "1. " + result
    lines = result.split("\n")
    characters = [l.split(". ", 1)[1].strip() for l in lines]
    return characters


@retry(count=8)
def get_location_category(location_name: str, builder_config: "DictConfig") -> str:
    """Provide the category of a location, from the set "self-contained", "generic", "composite", 'not a location' """
    final_prompt = LOCATION_TO_CATEGORY.format(location_name)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")
    result = result.lower().split("\n", 1)[0].strip()
    assert result in [
        "self-contained",
        "generic",
        "composite",
        "not a location",
    ], f"location category didn't exist, {result}"
    return result


@retry(count=8)
def split_composite_location(
    story_prompt: str, location_name: str, builder_config: "DictConfig"
) -> List[str]:
    """Given a composite location, provide a list of locations that would comprise it"""
    final_prompt = COMPOSITE_TO_COMPONENTS.format(story_prompt, location_name)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt, frequency_penalty=0.2)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = "1. " + result
    lines = result.split("\n")
    locations = [l.split(". ", 1)[1].strip() for l in lines]
    return locations


@retry(count=8)
def get_group_location_instances(
    story_prompt: str, location_name: str, builder_config: "DictConfig"
) -> List[str]:
    """Given a grouped location, provide some instances"""
    final_prompt = GROUPING_TO_INSTANCES.format(story_prompt, location_name)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = "1. " + result
    lines = result.split("\n")
    locations = [l.split(". ", 1)[1].strip() for l in lines]
    return locations


@retry(count=8)
def describe_location(
    story_prompt: str, location_name: str, builder_config: "DictConfig"
) -> Dict[str, str]:
    """Given a location, provide the description and backstory"""
    final_prompt = LOCATION_NAME_TO_DESCRIPTIONS.format(story_prompt, location_name)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    description, backstory = result.split("\nBackstory:")
    return {
        "description": description.strip(),
        "backstory": backstory.strip(),
    }


@retry(count=8)
def annotate_location(
    story_prompt: str,
    location_name: str,
    location_description: str,
    builder_config: "DictConfig",
) -> Dict[str, List[str]]:
    """Given a location and description, provide contents"""
    final_prompt = LOCATION_ANNOTATION.format(
        story_prompt, location_name, location_description
    )
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    characters, other = result.split("\nObjects:")
    if "Nearby Locations" in other:
        objects, locations = other.split("\nNearby Locations:")
    else:
        objects = other
        locations = "- None"
    return {
        "characters": [
            elem.strip("- ").strip()
            for elem in characters.strip().split("\n")
            if elem != "- None"
        ],
        "locations": [
            elem.strip("- ").strip()
            for elem in locations.strip().split("\n")
            if elem != "- None"
        ],
        "objects": [
            elem.strip("- ").strip()
            for elem in objects.strip().split("\n")
            if elem != "- None"
        ],
    }


@retry(count=8)
def annotate_prompted_character(
    story_prompt: str, character_name: str, builder_config: "DictConfig"
) -> Dict[str, List[str]]:
    """Given a character and the story they come from, annotate attributes"""
    final_prompt = PROMPTED_CHARACTER_ANNOTATION.format(story_prompt, character_name)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    singular, other = result.split("\nPlural Form:")
    plural, other = other.split("\nSingular Persona:")
    persona, other = other.split("\nSingular Physical Description:")
    description, other = other.split("\nSingular Motivation:")
    motivation, emoji = other.split("\nEmoji:")
    return {
        "singular": singular.strip(),
        "plural": plural.strip(),
        "persona": persona.strip(),
        "description": description.strip(),
        "motivation": motivation.strip(),
        "emoji": emoji.strip(),
        "carrying": [],
        "wielding": [],
        "wearing": [],
    }


@retry(count=8)
def annotate_set_character(
    location_description: str, character_name: str, builder_config: "DictConfig"
) -> Dict[str, List[str]]:
    """Given a character and the room they come from, annotate attributes AND contents"""
    final_prompt = ROOM_CHARACTER_ANNOTATION.format(
        location_description, character_name
    )
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    singular, other = result.split("\nPlural Form:")
    plural, other = other.split("\nSingular Persona:")
    persona, other = other.split("\nSingular Physical Description:")
    description, other = other.split("\nSingular Motivation:")
    motivation, other = other.split("\nEmoji:")
    emoji, other = other.split("\nCarrying:")
    carryings, other = other.split("\nWielding:")
    wieldings, wearings = other.split("\nWearing:")
    return {
        "singular": singular.strip(),
        "plural": plural.strip(),
        "persona": persona.strip(),
        "description": description.strip(),
        "motivation": motivation.strip(),
        "emoji": emoji.strip(),
        "carrying": [
            elem.strip("- ").strip()
            for elem in carryings.strip().split("\n")
            if elem != "- None"
        ],
        "wielding": [
            elem.strip("- ").strip()
            for elem in wieldings.strip().split("\n")
            if elem != "- None"
        ],
        "wearing": [
            elem.strip("- ").strip()
            for elem in wearings.strip().split("\n")
            if elem != "- None"
        ],
    }


@retry(count=8)
def annotate_object(
    object_name: str, builder_config: "DictConfig"
) -> Dict[str, List[str]]:
    """Given an object name, annotate it fully"""
    final_prompt = OBJECT_ANNOTATION.format(object_name)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    singular, other = result.split("\nPlural form:")
    plural, other = other.split("\nSingular description:")
    description, other = other.split("\nFood:")
    is_food, other = other.split("\nDrink:")
    is_drink, other = other.split("\nHoldable:")
    is_holdable, other = other.split("\nWearable:")
    is_wearable, other = other.split("\nWieldable:")
    is_wieldable, other = other.split("\nSurface:")
    is_surface, is_container = other.split("\nContainer:")
    return {
        "singular": singular.strip(),
        "plural": singular.strip(),
        "description": description.strip(),
        "is_food": is_food.strip() == "yes",
        "is_drink": is_drink.strip() == "yes",
        "is_holdable": is_holdable.strip() == "yes",
        "is_wearable": is_wearable.strip() == "yes",
        "is_wieldable": is_wieldable.strip() == "yes",
        "is_surface": is_surface.strip() == "yes",
        "is_container": is_container.strip() == "yes",
    }


@retry(count=8)
def get_neighbor_map(
    location_list: List[str], builder_config: "DictConfig"
) -> Dict[str, List[str]]:
    """Given an object name, annotate it fully"""
    noted_locations = [f"{idx + 1}. {loc}" for (idx, loc) in enumerate(location_list)]
    final_prompt = ROOM_NEIGHBORS.format("\n".join(noted_locations))
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = "1. " + result.strip()
    lines = result.split("\n")
    lines = [l for l in lines if len(l.strip()) > 0]
    items = [l.split(". ", 1)[1].split(": ") for l in lines]
    mapping = {l[0].lower().strip(): l[1].split(", ") for l in items}
    lower_list = [l.lower() for l in location_list]
    for loc in location_list:
        assert loc.lower() in mapping, f"{loc.lower()} not in mapping {mapping}"
        mapping[loc] = [t for t in mapping[loc] if t.lower() in lower_list]
    print(mapping)
    return mapping


class LLMPromptGraphBuilder(GraphBuilder):
    """Builds a one-room light Graph using a StarSpace model to connect everything."""

    CONFIG_CLASS = LLMPromptBuilderConfig

    def __init__(self, builder_config: "DictConfig"):
        """Initialize the LLM"""
        self.builder_config = builder_config
        if builder_config._backend == "openai":
            openai.organization = builder_config.openai_org_id
            openai.api_key = builder_config.openai_secret_key
        else:
            raise AssertionError(f"Unsupported backend {builder_config._backend}")

        self.possible_rooms: Dict[str, Dict[str, Any]] = {}  # room name to props
        self.possible_agents: Dict[str, Dict[str, Any]] = {}  # char name to props
        self.possible_items: Dict[str, Dict[str, Any]] = {}  # obj name to props

    def _spawn_agent_in_room(
        self, world: World, agent: "GraphAgent", room: "GraphRoom"
    ) -> None:
        """Spawn the given agent in the given room of the given world"""
        agent.move_to(room)
        arrival_event = ArriveEvent(
            agent, text_content=f"arrives from {random.choice(POSSIBLE_NEW_ENTRANCES)}"
        )
        arrival_event.execute(world)

    def _get_agent_to_respawn(self, world: World) -> Optional[str]:
        """Return an agent that once existed in this graph, but no longer does"""
        # Only spawn agents if they don't already exist
        agents_to_use = [
            a["singular"]
            for a in self.possible_agents.values()
            if len(world.oo_graph.find_nodes_by_name(a["singular"])) == 0
        ]
        if len(agents_to_use) == 0:
            return None

        return random.choice(agents_to_use)

    async def add_random_new_agent_to_graph(
        self, world: World
    ) -> Optional["GraphAgent"]:
        """
        Add an agent from the stored possible agents list that isn't
        currently present in the world, if such an agent exists.

        Return that agent if it is created, otherwise return None
        """
        possible_respawn_name = self._get_agent_to_respawn(world)
        if possible_respawn_name is None:
            return None

        g = world.oo_graph
        character = self.possible_agents[possible_respawn_name.lower()]
        if character["location"] is None:
            target_room = random.choice(all_room_nodes)
        else:
            target_room = character["location"]["node"]

        agent_node = g.add_agent(
            character["singular"],
            {
                "agent": True,
                "size": 20,
                "contain_size": 20,
                "health": 2,
                "food_energy": 1,
                "aggression": 0,
                "speed": 5,
                "char_type": "person",
                "name_prefix": character.get("name_prefix", "the"),
                "desc": character["description"],
                "persona": f"{character['persona']}",
                "mission": character["motivation"],
            },
        )
        character["node"] = agent_node
        object_names = character["carrying"]
        for object_name in object_names:
            obj = objects[object_name.lower()]
            object_node = g.add_object(
                obj["singular"],
                self._props_from_obj(obj),
            )
            object_node.move_to(agent_node)
        object_names = character["wearing"]
        for object_name in object_names:
            obj = objects[object_name.lower()]
            object_node = g.add_object(
                obj["singular"],
                self._props_from_obj(obj),
            )
            object_node.move_to(agent_node)
            object_node.equipped = "wear"
        object_names = character["wielding"]
        for object_name in object_names:
            obj = objects[object_name.lower()]
            object_node = g.add_object(
                obj["singular"],
                self._props_from_obj(obj),
            )
            object_node.move_to(agent_node)
            object_node.equipped = "wield"

        self._spawn_agent_in_room(world, agent_node, target_room)
        return agent_node

    def reset_graph(self) -> None:
        """Reset the current state of this builder before a rebuild"""
        self.possible_rooms = {}  # room name to props
        self.possible_agents = {}  # char name to props
        self.possible_items = {}  # obj name to props

    def _drop_articles(self, name_list: List[str]) -> List[str]:
        res = []
        for elem in name_list:
            elem = elem.strip()
            for article in ["a ", "an ", "the "]:
                if elem.lower().startswith(article):
                    elem = elem[len(article) :]
                    break
            res.append(elem)
        return res

    def _cleanup_names(self, name_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for elem in name_list:
            elem["name"] = elem["name"].strip()
            for article in ["a ", "an ", "the "]:
                if elem["name"].lower().startswith(article):
                    elem["name_prefix"] = article
                    elem["name"] = elem["name"][len(article) :]
            if "singular" in elem:
                elem["singular"] = elem["singular"].strip()
                for article in ["a ", "an ", "the "]:
                    if elem["singular"].lower().startswith(article):
                        elem["name_prefix"] = article
                        elem["singular"] = elem["singular"][len(article) :]
        return name_list

    def build_possible_locations(
        self, story_prompt: str, size: int
    ) -> Dict[str, Dict[str, Any]]:
        """
        Given a story prompt and desired world size, create at least that many
        possible rooms
        """
        base_locations = get_story_locations(story_prompt, self.builder_config)
        base_location_list = self._cleanup_names([{"name": n} for n in base_locations])
        completed_locations = []
        location_names = set()
        # iterate through the process of building locations until we hit the cap
        while len(location_names) < size and len(base_location_list) > 0:
            for location in base_location_list:
                location["category"] = get_location_category(
                    location["name"], self.builder_config
                )

            individuals = [
                l for l in base_location_list if l["category"] == "self-contained"
            ]
            composites = [l for l in base_location_list if l["category"] == "composite"]
            groupings = [l for l in base_location_list if l["category"] == "generic"]

            visible_neighbors = []
            # Create rooms for the individuals
            for i_room in individuals:
                i_room.update(
                    describe_location(story_prompt, i_room["name"], self.builder_config)
                )
                i_room.update(
                    annotate_location(
                        story_prompt,
                        i_room["name"],
                        i_room["description"],
                        self.builder_config,
                    )
                )
                i_room["neighbors"] = self._drop_articles(i_room["locations"])
                visible_neighbors += self._cleanup_names(
                    [{"name": n} for n in i_room["locations"]]
                )
                completed_locations.append(i_room)
                location_names.add(i_room["name"])
                print("r", end="", flush=True)
                if len(location_names) >= size + 10:
                    break

            if len(completed_locations) >= size:
                break

            # Break out composites into _potentially_ individual rooms
            broken_composites = []
            for composite in composites:
                c_name = composite["name"]
                composite_names = split_composite_location(
                    story_prompt, c_name, self.builder_config
                )
                # Pick random elements of the composite to be the neighbor suggestion
                clean_names = self._drop_articles(composite_names)
                for loc in completed_locations:
                    if "neighbors" in loc:
                        loc["neighbors"] = [
                            n if n != c_name else random.choice(clean_names)
                            for n in loc["neighbors"]
                        ]
                # Create the group of composite elements, where each is a neighbor for another
                composite_group = self._cleanup_names(
                    [
                        {
                            "name": n,
                            "neighbors": self._drop_articles(
                                [i for i in composite_names if i != n]
                            ),
                        }
                        for n in composite_names
                    ]
                )
                broken_composites += composite_group

            # Get instances for anything that is a group
            group_instances = []
            for group in groupings:
                g_name = group["name"]
                instance_names = get_group_location_instances(
                    story_prompt, g_name, self.builder_config
                )
                random.shuffle(instance_names)
                instance_names = instance_names[:3]
                clean_names = self._drop_articles(instance_names)
                for loc in completed_locations:
                    if "neighbors" in loc:
                        loc["neighbors"] = loc["neighbors"] = [
                            n if n != g_name else random.choice(clean_names)
                            for n in loc["neighbors"]
                        ]
                group_instances += self._cleanup_names(
                    [{"name": n} for n in instance_names]
                )

            # Determine candidate list from broken out components
            base_location_list = visible_neighbors + broken_composites + group_instances
            base_location_list = [
                bl for bl in base_location_list if bl["name"] not in location_names
            ]

        name_map = {l["name"].lower(): l for l in completed_locations}
        for location in name_map.values():
            location["neighbors"] = [n for n in location["neighbors"] if n in name_map]
        return name_map

    def get_possible_neighbors(self, loc: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = loc
        up_loc = (x, y - 1)
        down_loc = (x, y + 1)
        left_loc = (x - 1, y)
        right_loc = (x + 1, y)
        locs = [up_loc, down_loc, left_loc, right_loc]
        return locs

    def get_open_neighbors(
        self,
        grid: Dict[Tuple[int, int], Dict[str, Any]],
        loc: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        locs = self.get_possible_neighbors(loc)
        random.shuffle(locs)
        return [l for l in locs if grid.get(l) is None]

    def layout_locations(
        self,
        possible_locations: Dict[str, Dict[str, Any]],
        size: int,
    ) -> Dict[Tuple[int, int], Dict[str, Any]]:
        """Given a dict of possible locations, lay them out into a grid"""
        room_name_list = list(possible_locations.keys())
        neighbor_mapping = get_neighbor_map(room_name_list, self.builder_config)
        for room in possible_locations.values():
            room["neighbors"] += neighbor_mapping[room["name"].lower()]
        room_0 = list(possible_locations.values())[0]
        room_queue = [room_0]
        room_0["loc"] = (0, 0)
        room_0["linked_neighbors"] = []
        grid = {(0, 0): room_0}
        while len(grid) < size:
            # select next room to deal with
            if len(room_queue) != 0:
                room = room_queue.pop(0)
                loc = room["loc"]
                print("P", end="", flush=True)
            else:
                print("R", end="", flush=True)
                print("Random deets")
                unplaced_rooms = [
                    l for l in possible_locations.values() if l.get("loc") is None
                ]
                print("Unplaced rooms: ", unplaced_rooms)
                room = random.choice(unplaced_rooms)
                print(room, "Has linkable neighbor?")
                linkable_neighbors = [
                    possible_locations[n.lower()]
                    for n in room["neighbors"]
                    if possible_locations[n.lower()].get("loc") is not None
                ]
                print(linkable_neighbors)
                print(
                    [
                        self.get_open_neighbors(grid, l["loc"])
                        for l in linkable_neighbors
                    ]
                )
                usable_neighbors = [
                    l
                    for l in linkable_neighbors
                    if len(self.get_open_neighbors(grid, l["loc"])) > 0
                ]
                if len(usable_neighbors) == 0:
                    print("ER", end="", flush=True)
                    usable_neighbors = [
                        l
                        for l in list(grid.values())
                        if len(self.get_open_neighbors(grid, l["loc"])) > 0
                    ]
                print("Usable:", usable_neighbors)
                neighbor_room = random.choice(usable_neighbors)
                loc = random.choice(self.get_open_neighbors(grid, neighbor_room["loc"]))
                room["loc"] = loc
                grid[loc] = room
                room["linked_neighbors"] = [neighbor_room["loc"]]

            # possibly add neighbors to that room, add them to the queue
            neighbor_names = [
                n
                for n in room["neighbors"]
                if possible_locations[n.lower()].get("loc") is None
            ]
            open_locs = self.get_open_neighbors(grid, loc)

            for n, n_loc in zip(neighbor_names, open_locs):
                neighbor_room = possible_locations[n.lower()]
                neighbor_room["linked_neighbors"] = [loc]
                room["linked_neighbors"].append(n_loc)
                neighbor_room["loc"] = n_loc
                room_queue.append(neighbor_room)
                grid[n_loc] = neighbor_room
                print("n", end="", flush=True)

        # possibly connect neighbors that aren't
        for loc, room in grid.items():
            possible_neighbor_locs = self.get_possible_neighbors(loc)
            neighbor_rooms = [
                grid.get(l) for l in possible_neighbor_locs if grid.get(l) is not None
            ]
            for n_room in neighbor_rooms:
                if n_room["loc"] in room["linked_neighbors"]:
                    continue
                if (
                    room["name"] in n_room["neighbors"]
                    or n_room["name"] in room["neighbors"]
                ):
                    n_room["linked_neighbors"].append(loc)
                    room["linked_neighbors"].append(n_room["loc"])
                    print("u", end="", flush=True)

        return grid

    def build_possible_characters(
        self, story_prompt: str, locations: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create the dictionary of possible characters based on the
        story prompt and locations
        """
        base_character_names = get_story_characters(story_prompt, self.builder_config)
        additional_characters = []
        for location in locations:
            additional_characters += [
                {"name": c, "location": location} for c in location["characters"]
            ]
        additional_characters = self._cleanup_names(additional_characters)

        for a_char in additional_characters:
            a_char.update(
                annotate_set_character(
                    a_char["location"]["description"],
                    a_char["name"],
                    self.builder_config,
                )
            )

        base_characters = self._cleanup_names(
            [{"name": n} for n in base_character_names]
        )
        for b_char in base_characters:
            b_char.update(
                annotate_prompted_character(
                    story_prompt, b_char["name"], self.builder_config
                )
            )
            b_char["location"] = None

        all_chars = base_characters + additional_characters
        return {c["name"].lower(): c for c in all_chars}

    def build_possible_objects(
        self,
        characters: Dict[str, Dict[str, Any]],
        locations: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create the dictionary of possible objects based on the
        story prompt and locations
        """
        # Extract in-room objects
        room_objects = []
        for location in locations:
            room_objects += [
                {"name": obj, "location": location} for obj in location["objects"]
            ]

        # Extract in-character objects
        char_objs = []
        for character in characters.values():
            local_objs = (
                character["carrying"] + character["wearing"] + character["wielding"]
            )
            char_objs += [{"name": obj, "location": character} for obj in local_objs]

        all_objs = self._cleanup_names(room_objects + char_objs)
        for obj in all_objs:
            obj.update(annotate_object(obj["name"], self.builder_config))
        all_objs = self._cleanup_names(all_objs)
        return {obj["name"].lower(): obj for obj in all_objs}

    def _props_from_obj(self, obj):
        """Extract the relevant props from an obj"""
        use_classes = ["object"]
        props = {
            "object": True,
            "size": 1,
            "food_energy": 0,
            "value": 1,
            "desc": obj["description"],
            "name_prefix": obj.get("name_prefix", "the"),
        }
        if obj["is_surface"]:
            props["container"] = True
            props["size"] = 4
            props["contain_size"] = 3
            props["surface_type"] = "on"
            use_classes.append("container")
        if obj["is_container"] > 0.5:
            props["container"] = True
            props["size"] = 4
            props["contain_size"] = 3
            props["surface_type"] = "on"
            use_classes.append("container")
        if obj["is_drink"]:
            props["drink"] = True
            props["food_energy"] = 1
            use_classes.append("drink")
        if obj["is_food"]:
            props["food"] = True
            props["food_energy"] = 2
            use_classes.append("food")
        if not obj["is_holdable"]:
            use_classes.append("not_gettable")
        if obj["is_wearable"]:
            props["wearable"] = True
            props["stats"] = {"defense": 1}
            use_classes.append("wearable")
        if obj["is_wieldable"]:
            props["wieldable"] = True
            props["stats"] = {"attack": 1}
            use_classes.append("wieldable")

        props["classes"] = use_classes
        props["is_plural"] = False

        return props

    def assemble_graph(
        self,
        story_prompt: str,
        grid: Dict[Tuple[int, int], Dict[str, Any]],
        characters: Dict[str, Dict[str, Any]],
        objects: Dict[str, Dict[str, Any]],
        num_characters: int,
    ) -> OOGraph:
        """Construct a graph based on the provided possible elements"""
        g = OOGraph(title=story_prompt)

        room_map = {r["name"]: r for r in grid.values()}

        # create the rooms
        for room in grid.values():
            room_node = g.add_room(
                room["name"],
                {
                    "room": True,
                    "desc": room["description"],
                    "extra_desc": room["backstory"],
                    "size": 2000,
                    "contain_size": 2000,
                    "name_prefix": "the",
                    "surface_type": "in",
                    "classes": {"room"},
                },
            )
            room["node"] = room_node

        # create the neighbor relationships
        for room in grid.values():
            # only address north and east neighbors, if they exist
            x, y = room["loc"]
            north = (x, y - 1)
            east = (x + 1, y)
            if north in room["linked_neighbors"]:
                g.add_paths_between(
                    room["node"],
                    grid[north]["node"],
                    "a path to the north",
                    "a path to the south",
                )
            if east in room["linked_neighbors"]:
                g.add_paths_between(
                    room["node"],
                    grid[east]["node"],
                    "a path to the east",
                    "a path to the west",
                )

        all_room_nodes = [r["node"] for r in grid.values()]

        # Now place characters. Place top 5 story in random locations,
        # then choose randomly between in-room and story to place
        # in appropriate locations
        story_characters = [c for c in characters.values() if c["location"] is None]
        added_char_names = set()
        added_chars = []
        while len(added_chars) < min(num_characters, len(characters)):
            if len(added_chars) < 5:
                target_char = story_characters.pop(0)
            else:
                target_char = random.choice(
                    [
                        c
                        for c in characters.values()
                        if c["singular"] not in added_char_names
                    ]
                )
            if target_char["location"] is None:
                target_room = random.choice(all_room_nodes)
            else:
                target_room = target_char["location"]["node"]

            agent_node = g.add_agent(
                target_char["singular"],
                {
                    "agent": True,
                    "size": 20,
                    "contain_size": 20,
                    "health": 2,
                    "food_energy": 1,
                    "aggression": 0,
                    "speed": 5,
                    "char_type": "person",
                    "name_prefix": target_char.get("name_prefix", "the"),
                    "desc": target_char["description"],
                    "persona": f"{target_char['persona']}",
                    "mission": target_char["motivation"],
                },
            )
            added_char_names.add(target_char["singular"])
            target_char["node"] = agent_node
            added_chars.append(target_char)
            agent_node.move_to(target_room)

        # Add room objects
        for room in room_map.values():
            object_names = room["objects"]
            for object_name in object_names:
                obj = objects[object_name.lower()]
                object_node = g.add_object(
                    obj["singular"],
                    self._props_from_obj(obj),
                )
                object_node.move_to(room["node"])

        # add character objects
        for char in added_chars:
            object_names = char["carrying"]
            for object_name in object_names:
                obj = objects[object_name.lower()]
                object_node = g.add_object(
                    obj["singular"],
                    self._props_from_obj(obj),
                )
                object_node.move_to(char["node"])
            object_names = char["wearing"]
            for object_name in object_names:
                obj = objects[object_name.lower()]
                object_node = g.add_object(
                    obj["singular"],
                    self._props_from_obj(obj),
                )
                object_node.move_to(char["node"])
                object_node.equipped = "wear"
            object_names = char["wielding"]
            for object_name in object_names:
                obj = objects[object_name.lower()]
                object_node = g.add_object(
                    obj["singular"],
                    self._props_from_obj(obj),
                )
                object_node.move_to(char["node"])
                object_node.equipped = "wield"

        return g

    def build_graph(self, prompt: str) -> OOGraph:
        """Build a graph from the given prompt"""
        self.reset_graph()

        # Get possible locations
        print("Generating rooms:")
        possible_locations = self.build_possible_locations(
            prompt, self.builder_config.num_rooms
        )

        # Create layout
        print("\nCreating Grid layout:")
        grid = self.layout_locations(possible_locations, self.builder_config.num_rooms)
        used_locations = list(grid.values())

        # Get possible characters, based only on used rooms
        print("\nGenerating Characters:")
        possible_characters = self.build_possible_characters(prompt, used_locations)

        # Get possible objects
        print("\nGenerating Objects:")
        possible_objects = self.build_possible_objects(
            possible_characters, used_locations
        )

        print("\nBuilding Graph:")
        graph = self.assemble_graph(
            prompt,
            grid,
            possible_characters,
            possible_objects,
            self.builder_config.num_characters,
        )

        self.possible_agents = possible_characters
        self.possible_rooms = possible_locations
        self.possible_items = possible_objects
        return graph

    async def get_graph(
        self, world_config: WorldConfig
    ) -> Tuple[Optional["OOGraph"], Optional["World"]]:
        """Return an OOGraph built by this builder"""
        prompt = self.builder_config.prompt
        if prompt == "":
            raise AssertionError("Unprompted Generations not yet supported")

        attempts = 9
        graph = None
        world = None
        while graph is None and attempts > 0:
            try:
                random.seed(time.time())
                graph = self.build_graph(prompt)
                world = World(self._get_attached_config(world_config))
                world.oo_graph = g
                return graph, world
            except Exception as _e:
                print(_e)
                attempts -= 1
        return None, None

    def _get_attached_config(self, world_config: WorldConfig) -> WorldConfig:
        """
        Get a copy of the given world config attached to this builder
        """
        world_config = world_config.copy()
        world_config.graph_builder = self
        return world_config


if __name__ == "__main__":
    import os
    from light import LIGHT_DIR

    print("Welcome to the LLM world generator")

    print("Assuming openai backend, as only available")
    backend = "openai"

    if backend == "openai":
        org_id = input("Provide openai Org ID: ")
        openai_sk = input("Provide openai Secret Key: ")
        config = GPT3LLMBuilderConfig(openai_org_id=org_id, openai_secret_key=openai_sk)
    else:
        raise AssertionError(f"Backend {backend} not available")

    map_dir = os.path.join(LIGHT_DIR, "scripts", "examples", "maps")
    while True:
        prompt = input("Provide world prompt! Leave blank to quit.\n> ").strip()
        if len(prompt) == 0:
            break

        config.prompt = prompt
        config.num_rooms = int(input("Num Rooms:\n> "))
        config.num_characters = int(input("Num Chars:\n> "))

        builder = LLMPromptGraphBuilder(config)
        graph = builder.build_graph(prompt)

        output_name = input("\nProvide output name:\n>") + ".json"
        output_dir = os.path.join(map_dir, output_name)
        with open(output_dir, "w+") as json_file:
            json_file.write(graph.to_json())
        print(f"Written to {output_dir}")
        break
    print("Bye!")
