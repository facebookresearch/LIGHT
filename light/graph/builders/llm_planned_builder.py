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
from light.graph.builders.llm_prompt_builder import (
    LLMPromptBuilderConfig,
    GPT3LLMBuilderConfig,
)
from light.graph.structured_graph import OOGraph
from light.world.world import World, WorldConfig

from functools import wraps
from omegaconf import MISSING, DictConfig
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from light.graph.elements.graph_nodes import (
        GraphRoom,
        GraphNode,
        NodeProps,
        GraphAgent,
    )


class Area(TypedDict):
    name: str
    context: str
    description: str
    backstory: str
    processed: bool
    shared: Optional[Tuple[str, str]]
    neighbors: List["Area"]
    subareas: Dict[str, "Area"]
    edges: List[Tuple[str, str]]


DEFAULT_PUNC = [",", ".", "!", "?", ":"]


def clean_strip(s, punc=DEFAULT_PUNC):
    s = s.strip()
    for p in punc:
        s = s.strip(p)
    return s


def no_list(s):
    """Remove list lead-ins for the given string"""
    return clean_strip(s.split(".", 1)[1])


RATE_LIMIT_PER_MIN = 1000
DELAY_TIME = 60.0 / RATE_LIMIT_PER_MIN
last_query_time = time.time()
last_query = "No Query Yet"


def query_openai(
    prompt: str,
    temperature: float = 0.7,
    top_p: float = 1.0,
    frequency_penalty: float = 0,
    presence_penalty: float = 0,
):
    """Wrapper around openai queries, with some parameters"""
    global last_query
    global last_query_time
    now = time.time()
    if now - last_query_time < DELAY_TIME:
        time.sleep(DELAY_TIME - (now - last_query_time))
    last_query_time = now
    completion = openai.Completion.create(
        engine="text-davinci-003",
        temperature=temperature,
        top_p=top_p,
        prompt=prompt,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_tokens=1000,
    )
    last_query = f"Prompt: {prompt}\nGeneration: {completion.choices[0].text.strip()}"
    print(".", end="", flush=True)
    return completion.choices[0].text.strip()


def retry(count=5, exc_type=Exception):
    def decorator(func):
        @wraps(func)
        def result(*args, **kwargs):
            ret_exec = None
            for _i in range(count):
                try:
                    return func(*args, **kwargs)
                except exc_type as e:
                    ret_exec = e
                    print("e", end="", flush=True)
            print("Exception Query:\n" + last_query)
            print(ret_exec)
            raise ret_exec

        return result

    return decorator


PROMPT_FOR_PLAN = """Let's try to create a text adventure game environment, based on the prompt: "{}"

Provide 5-6 paragraphs of background context extending this prompt that we can use to make the setting, characters, and objects inside both interesting and consistent. Include details about specific important locations, characters, and key items. Try to name important characters as well. Make up extensions to the prompt if necessary.

"""


@retry(count=7)
def create_plan_from_prompt(
    story_prompt: str,
    builder_config: "DictConfig",
) -> List[str]:
    """Get a list of story locations given a related story prompt"""
    final_prompt = PROMPT_FOR_PLAN.format(story_prompt)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")
    result = result.strip()
    return result


PLAN_TO_AREAS = """​​I'm writing a text adventure game. This is the background story of the game:
""
{}
""
The key locations or settings for this story are as follows. Provide only the name of the location. Feel free to come up with additional *locations* as necessary:
1."""
AREA_CAP = 7


@retry(count=7)
def get_areas_from_plan(
    story_plan: str,
    builder_config: "DictConfig",
) -> List[str]:
    """Get a list of story locations given a related story prompt"""
    final_prompt = PLAN_TO_AREAS.format(story_plan)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")
    result = "1." + result

    result = [no_list(l) for l in result.split("\n") if len(l.strip())]
    return result[:AREA_CAP]


AREAS_TO_ROOMS = """
​​I'm writing a text adventure game. This is the background story of the game:
""
{}
""
The key locations for this story are as follows:
{}

Provide a list of up to ~20 text adventure room sub-locations that will be present in a text adventure game with the above backstory, split over the above regions.  The format should be:
1. Key Location
  a. sub-location within key location
  b. sub-location within key location
2. Key Location
3. ...

Don't use leading articles. Be specific:
1."""


def strip_articles(txt):
    for article in ["a ", "an ", "the "]:
        if txt.lower().startswith(article):
            return txt[len(article) :], article.strip()
    return txt, None


@retry(count=7)
def get_area_room_map_from_plan(
    story_plan: str,
    areas: List[str],
    builder_config: "DictConfig",
) -> Dict[str, List[str]]:
    """Get a list of story locations given a related story prompt"""
    final_prompt = AREAS_TO_ROOMS.format(story_plan, areas)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = "1." + result
    result = [l.strip() for l in result.split("\n") if len(l.strip())]
    result_map = {a: [] for a in areas}
    last_key = None
    for l in result:
        if l[0].isdigit():
            l = no_list(l)
            assert l in result_map, f"{l} not a key in {result_map.keys()}"
            last_key = l
        else:
            result_map[last_key].append(strip_articles(no_list(l))[0])
    for loc, sublocs in result_map.items():
        assert len(sublocs) > 0, f"No sublocs created for {loc}"
    return result_map


def room_map_to_areas(room_map: Dict[str, List[str]]) -> Dict[str, Area]:
    """Compress the result of the room map into Area dicts"""
    area_list = {}
    for area_name, subarea_list in room_map.items():
        area_list[area_name] = {
            "name": area_name,
            "description": "",
            "backstory": "",
            "processed": False,
            "shared": None,
            "neighbors": [],
            "subareas": {
                n: {
                    "name": n,
                    "description": "",
                    "backstory": "",
                    "processed": False,
                    "shared": None,
                    "neighbors": [],
                    "subareas": {},
                }
                for n in subarea_list
            },
        }
    return area_list


ARRANGE_SUBAREAS = """
​​I'm writing a text adventure game. This is the background story of the game:

""
{}
""

The full list of areas are as follows:
{}

For each of the above main areas, if they are actually sub-area of another main area write the exact name of the area they are a part of. Otherwise, write "not a sub-area". Use the format "1. <area> - <answer>":
1."""


@retry(count=7)
def get_subarea_mapping(
    story_plan: str,
    areas: List[str],
    builder_config: "DictConfig",
) -> Dict[str, List[str]]:
    """Convert a flat map for the areas in a game into a graph"""
    final_prompt = ARRANGE_SUBAREAS.format(story_plan, areas)
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = "1." + result
    result = [no_list(l) for l in result.split("\n") if len(l.strip())]

    pairs = [l.split(" - ") for l in result]
    for p in pairs:
        assert p[0] in areas, f"Area {p[0]} not in areas..."
        assert (
            p[1] in areas or p[1].lower() == "not a sub-area"
        ), f"Area {p[1]} not in areas..."
    out_areas = set(p[0] for p in pairs)
    for area in areas:
        assert area in out_areas, f"Area {area} not in out areas {out_areas}"

    container_areas = set(p[1] for p in pairs if p[1].lower() != "not a sub-area")
    subarea_map = {c: [] for c in container_areas}
    for p in pairs:
        if p[1].lower() == "not a sub-area":
            continue
        subarea_map[p[1]].append(p[0])

    return subarea_map


def apply_subarea_mapping(
    area_map: Dict[str, Area], subarea_mapping: Dict[str, List[str]]
) -> Dict[str, Area]:
    """Apply a subarea mapping to a given area map"""
    # Create a mapping of targetted subareas
    temp_mapping = {}
    for area, subareas in subarea_mapping.items():
        for subarea in subareas:
            temp_mapping[subarea] = area_map[subarea]

    # Retain subareas not affected by the given mapping
    new_mapping = {
        a: area
        for a, area in area_map.items()
        if a not in subarea_mapping and a not in temp_mapping
    }
    # Apply the new mapping
    for area, subareas in subarea_mapping.items():
        if area not in temp_mapping:
            new_mapping[area] = area_map[area]
        for subarea in subareas:
            area_map[area]["subareas"][subarea] = temp_mapping[subarea]
    return new_mapping


MAIN_AREA_LINK = """
​​I'm writing a text adventure game, and am trying to determine how locations connect. This is the background story of the game:

""
{}
""

The main locations are:
{}

The list of possible connection pairs is:
{}


For each pair, determine if based on the story the two should be reasonably connected? If so, provide the name of a transition location that connects the two and the reason that sublocation connects the two, in the format <name> - <reason>. If they are very far apart, or require traveling through one of the other listed areas, write "these don't directly connect" instead.
Note that while each location must connect to one other, none should connect to ALL of them.
Please don't reuse connecting sublocation names.

Answer:
{} -"""


@retry(count=7)
def link_main_areas(
    story_plan: str,
    areas: List[str],
    builder_config: "DictConfig",
) -> Dict[Tuple[str, str], Optional[str]]:
    """From the story plan, determine connecting rooms"""
    areas_text = "\n".join(["- " + a for a in areas])

    area_pairs = {}
    for idx, area1 in enumerate(areas):
        for area2 in areas[idx + 1 :]:
            area_pairs[(area1, area2)] = None

    if len(area_pairs) == 0:
        return area_pairs

    seen_edges = []

    seen_edge_text = "None"

    pairs_text = "\n".join([f"({a1}, {a2})" for (a1, a2) in area_pairs.keys()])
    edge_prompt = MAIN_AREA_LINK.format(
        story_plan, areas_text, pairs_text, pairs_text.split("\n")[0]
    )
    if builder_config._backend == "openai":
        result = query_openai(edge_prompt, temperature=0.22)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = "(,) - " + result.strip()
    result_lines = result.split("\n")
    result_lines = [l.strip() for l in result_lines if len(l.strip())]
    assert len(result_lines) == len(
        area_pairs
    ), f"Not equal lines as possible pairs: {result_lines}, {area_pairs}"
    for idx, k in enumerate(list(area_pairs.keys())):
        result_line = result_lines[idx]
        entry = result_line.split(" - ")[1]
        assert len(entry) < 40, f"Provided entry too long! {entry}"
        if entry.lower().startswith("these don't directly connect"):
            continue

        area_pairs[k] = entry
    return area_pairs


def add_links(
    area_map: Dict[str, Area], links: Dict[Tuple[str, str], str]
) -> Dict[str, Area]:
    """Apply links to an area map, adding linked locations to both lists"""
    for ((a1, a2), v) in links.items():
        if v is None:
            continue
        new_loc = {
            "name": v,
            "description": "",
            "backstory": "",
            "processed": False,
            "shared": (a1, a2),
            "neighbors": [],
            "subareas": {},
        }
        area_map[a1]["subareas"][v] = new_loc
        area_map[a2]["subareas"][v] = new_loc
    return area_map


AREA_DEDUPE = """​​I'm building out a text adventure game map. Here's a provided section of the map with some subsections:

Location: {}
{}

We want to deduplicate this list. Please provide a version of the list after deduplicating. When two entries are similar, retain the earlier one. Use the exact same wording.

Location: {}
-"""


@retry(count=7)
def deduplicate_main_area(
    area_title: str,
    subareas: List[str],
    builder_config: "DictConfig",
) -> List[str]:
    """Deduplicate subareas from the main area"""
    subarea_text = "\n".join(["- " + a for a in subareas])

    final_prompt = AREA_DEDUPE.format(area_title, subarea_text, area_title)
    if builder_config._backend == "openai":
        result = "\n- " + query_openai(final_prompt, temperature=0.3)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = result.split("\n- ")[1:]
    for r in result:
        assert r in subareas, f"Subarea {r} returned not in {subareas}"

    return result


def deduplicate_all_main_areas(
    area_map: Dict[str, Area],
    builder_config: "DictConfig",
) -> Dict[str, Area]:
    """Runs deduplicate for all main areas, does alter base"""
    all_areas = list(area_map.values())
    while len(all_areas) > 0:
        curr_area = all_areas.pop(0)

        # Create priority list of subareas
        subareas = list(curr_area["subareas"].values())
        with_subareas = [s for s in subareas if len(s["subareas"]) > 0]
        no_subareas = [s for s in subareas if len(s["subareas"]) == 0]
        shared = [s for s in no_subareas if s["shared"] is not None]
        unshared = [s for s in no_subareas if s["shared"] is None]
        sorted_subareas = with_subareas + shared + unshared

        # Run deduplication
        areas_before = [s["name"] for s in sorted_subareas]
        deduplicated_names = deduplicate_main_area(
            curr_area["name"],
            [s["name"] for s in sorted_subareas],
            builder_config,
        )
        curr_area["subareas"] = {
            s_name: s
            for s_name, s in curr_area["subareas"].items()
            if s_name in deduplicated_names
        }

        # Add any remaining complex areas to the processing
        remaining_with_subareas = [
            s for s in with_subareas if s["name"] in deduplicated_names
        ]
        all_areas += remaining_with_subareas
    return area_map


ARRANGE_SUB_SUB_AREAS = """I'm building out a text adventure game map based on the following story:
""
{}
""

This is the list of subsections contained in one region of the map:
{}

For each of the above entries, if they are actually sub-area of another entry *in the above list* note the entry they are a part of using the exact same wording. Otherwise, write "not a sub-area"
- {} -"""


@retry(count=7)
def get_subsubarea_mapping(
    story_plan: str,
    area_title: str,
    subareas: List[str],
    builder_config: "DictConfig",
) -> Dict[str, List[str]]:
    """Convert a flat map for a subarea into a graph"""
    subarea_text = "\n".join(["- " + a for a in subareas])

    # final_prompt = ARRANGE_SUB_SUB_AREAS.format(story_plan, area_title, subarea_text, subareas[0])
    final_prompt = ARRANGE_SUB_SUB_AREAS.format(story_plan, subarea_text, subareas[0])
    if builder_config._backend == "openai":
        result = query_openai(final_prompt, temperature=0.1)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = f"\n- {subareas[0]} - " + result

    result = [l.strip() for l in result.split("\n- ") if len(l.strip())]

    pairs = [l.split(" - ") for l in result]
    for p in pairs:
        assert p[0] in subareas + [area_title], f"Area {p[0]} not in areas..."
        assert (
            p[1] in subareas or p[1].lower() == "not a sub-area"
        ), f"Area {p[1]} not in areas..."
    out_areas = set(p[0] for p in pairs)
    for area in subareas:
        assert area in out_areas, f"Area {area} not in out areas {out_areas}"

    container_areas = set(p[1] for p in pairs if p[1].lower() != "not a sub-area")
    subarea_map = {c: [] for c in container_areas}
    for p in pairs:
        if p[1].lower() == "not a sub-area" or p[1] == area_title:
            continue
        subarea_map[p[1]].append(p[0])

    return subarea_map


def run_subsubarea_mapping(
    story_plan: str,
    area_map: Dict[str, Area],
    builder_config: "DictConfig",
) -> Dict[str, Area]:
    """Run subsubarea mapping for all nodes in the graph"""
    all_areas = list(area_map.values())
    subarea_targets = list(area_map.values())
    for curr_area in all_areas:
        # Create list of subareas with subsubareas
        subareas = list(curr_area["subareas"].values())
        subarea_targets += [s for s in subareas if len(s["subareas"]) > 0]

    while len(subarea_targets) > 0:
        curr_area = subarea_targets.pop(0)

        # Run mapping
        subareas = list(curr_area["subareas"].values())
        subarea_names = [s["name"] for s in subareas]
        subarea_mapping = get_subsubarea_mapping(
            story_plan,
            curr_area["name"],
            subarea_names,
            builder_config,
        )
        curr_area["subareas"] = apply_subarea_mapping(
            curr_area["subareas"], subarea_mapping
        )

        # Add new subsubarea targets
        subareas = list(curr_area["subareas"].values())
        subarea_targets += [s for s in subareas if len(s["subareas"]) > 0]
    return area_map


MAP_SUBLOCATIONS = """​I'm building out a text adventure game map based on the following story:
""
{}
""

This is the list of sublocations contained in "{}":
{}

For each sublocation, provide which other locations in the list that sublocation is physically connected with, in the format "- sublocation - comma separeted list of connected sublocations". Use exact spelling for sublocations, and only use other entries in the list. Every location must have at least one neighbor:

- {} -"""


@retry(count=7)
def map_subarea(
    story_plan: str,
    area_title: str,
    subareas: List[str],
    builder_config: "DictConfig",
) -> Dict[str, List[str]]:
    """Convert a flat map for the areas in a game into a graph"""
    if len(subareas) == 1:
        return {subareas[0]: []}
    subarea_text = "\n".join(["- " + a for a in subareas])

    final_prompt = MAP_SUBLOCATIONS.format(
        story_plan, area_title, subarea_text, subareas[0]
    )
    if builder_config._backend == "openai":
        result = query_openai(final_prompt, temperature=0.3)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = f"\n- {subareas[0]} - " + result

    result = [l.strip() for l in result.split("\n- ") if len(l.strip())]

    pairs = [l.split(" - ") for l in result]
    out_areas = set(p[0] for p in pairs)
    for area in subareas:
        assert area in out_areas, f"Area {area} not in out areas {out_areas}"

    neighbor_map = {p[0]: list(set(p[1].split(", "))) for p in pairs}
    for p in neighbor_map.values():
        for dest in p:
            assert dest in subareas, f"Subarea neighbor {dest} not found in {subareas}"

    return neighbor_map


def run_subarea_neighboring(
    story_plan: str,
    area_map: Dict[str, Area],
    builder_config: "DictConfig",
) -> Dict[str, Area]:
    """Run subarea neighboring for all nodes in the graph"""
    all_areas = list(area_map.values())
    subarea_targets = list(area_map.values())
    for curr_area in all_areas:
        # Create list of subareas with subsubareas
        subareas = list(curr_area["subareas"].values())
        subarea_targets += [s for s in subareas if len(s["subareas"]) > 0]

    while len(subarea_targets) > 0:
        curr_area = subarea_targets.pop(0)

        # Run mapping
        subareas = list(curr_area["subareas"].values())
        subarea_names = [s["name"] for s in subareas]
        neighbor_map = map_subarea(
            curr_area["context"],
            curr_area["name"],
            subarea_names,
            builder_config,
        )
        for subarea_name, neighbors in neighbor_map.items():
            subarea = curr_area["subareas"][subarea_name]
            previous_neighbors = subarea.get("neighbors", [])
            previous_neighbor_names = [n["name"] for n in previous_neighbors]

            new_neighbor_areas = [
                curr_area["subareas"][n]
                for n in neighbors
                if n not in previous_neighbor_names
            ]
            combined_neighbor_list = previous_neighbors + new_neighbor_areas

            subarea["neighbors"] = combined_neighbor_list

        # Add new subsubarea targets
        subareas = list(curr_area["subareas"].values())
        subarea_targets += [s for s in subareas if len(s["subareas"]) > 0]
    return area_map


# This query should produce a Description and Backstory for the given location name.
MAIN_LOCATION_TO_CONTEXT = """I'm building out a text adventure game map based on the following story:
""
{}
""

One section of the setting is "{}", and it has the following subareas:
{}

Provide 2-3 paragraphs of context for this area, it's layout, and the importance in the story. Don't make up locations not in the above list of subareas:
"""


@retry(count=7)
def describe_area(
    story_plan: str,
    location_name: str,
    subareas: List[str],
    builder_config: "DictConfig",
) -> str:
    """Given an area of the map, provide more context/planning for it"""
    subarea_text = "\n".join(["- " + a for a in subareas])
    final_prompt = MAIN_LOCATION_TO_CONTEXT.format(
        story_plan, location_name, subarea_text
    )
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    return result.strip()


def describe_all_main_areas(
    story_plan: str,
    area_map: Dict[str, Area],
    builder_config: "DictConfig",
) -> Dict[str, Area]:
    """Run subcontext generation for all main areas"""
    all_areas = list(area_map.values())
    subarea_targets = list(area_map.values())
    for curr_area in all_areas:
        # Create list of subareas with subsubareas
        subareas = list(curr_area["subareas"].values())
        subarea_targets += [s for s in subareas if len(s["subareas"]) > 0]

    while len(subarea_targets) > 0:
        curr_area = subarea_targets.pop(0)

        # Run context generation
        subareas = list(curr_area["subareas"].values())
        subarea_names = [s["name"] for s in subareas]
        context = describe_area(
            story_plan,
            curr_area["name"],
            subarea_names,
            builder_config,
        )
        curr_area["context"] = context

        # Add new subsubarea targets
        subarea_targets += [s for s in subareas if len(s["subareas"]) > 0]
    return area_map


LOCATION_NAME_TO_DESCRIPTIONS = """I'm building out a text adventure game map based on the following story:
""
{}
""

Given a location name and context of a medieval fantasy story it is supposed to appear in, provide both a text-adventure-style description and backstory in third-person perspective. The description should include characters and objects that may be found inside, narrated as if the person is reporting what it looks like when present there. The backstory should be flavor text about how the location came to be. The format is below.

Location: <the location's name>
Description: <a few sentences describing the location>
Backstory: <a few sentences describing context for the location>

Provide 4-7 sentences for the backstory and description.

The context for the surrounding area is:
""
{}
""
The location to describe is {}


Location: {}
Description:"""


@retry(count=7)
def describe_location(
    story_plan: str,
    area_prompt: str,
    location_name: str,
    neighbors: List[str],
    builder_config: "DictConfig",
) -> Dict[str, str]:
    """Given a location, provide the description and backstory"""
    neighbor_string = ", ".join(neighbors)
    final_prompt = LOCATION_NAME_TO_DESCRIPTIONS.format(
        story_plan, area_prompt, location_name, location_name
    )
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    description, backstory = result.split("\nBackstory:")
    return {
        "description": description.strip(),
        "backstory": backstory.strip(),
    }


def describe_all_locations(
    story_plan: str,
    area_map: Dict[str, Area],
    builder_config: "DictConfig",
) -> Dict[str, Area]:
    """Add descriptions and back stories to all of the locations in the map"""
    all_areas = list(area_map.values())
    while len(all_areas) > 0:
        curr_area = all_areas.pop(0)
        area_context = curr_area["context"]

        subareas = list(curr_area["subareas"].values())
        for subarea in subareas:
            if len(subarea["description"]):
                continue
            use_context = area_context
            use_name = subarea["name"]
            if subarea["shared"] is not None:
                a1, a2 = subarea["shared"]
                use_context = f"This area connects {a1} and {a2}"
            if len(subarea["subareas"]) > 0:
                use_name += " (outside)"

            resp = describe_location(
                story_plan,
                use_context,
                use_name,
                [n["name"] for n in subarea["neighbors"]],
                builder_config,
            )
            subarea.update(resp)

        all_areas += [s for s in subareas if len(s["subareas"]) > 0]
    return area_map


AREA_TO_SUBAREAS = """I'm building out a text adventure game map.

Consider the location {}:
The areas within are:
{}

After following "You enter {}", which of the listed areas makes the most sense to end up in? Provide just the name, no explanation:
"""


@retry(count=7)
def determine_entrance(
    location_name: str, subareas: List[str], builder_config: "DictConfig"
) -> str:
    """Given a location, provide the description and backstory"""
    random.shuffle(subareas)
    subarea_string = "\n- ".join(subareas)
    final_prompt = AREA_TO_SUBAREAS.format(
        location_name + " (outside)", subarea_string, location_name
    )
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = result.strip()
    assert result in subareas, f"Returned result {result} not in {subareas}"
    return result


def mark_all_entrances(
    area_map: Dict[str, Area],
    builder_config: "DictConfig",
) -> Dict[str, Area]:
    """For subareas with subsubareas, determine what the outside-inside border is"""
    all_areas = list(area_map.values())
    subarea_targets = []
    for curr_area in all_areas:
        # Create list of subareas with subsubareas
        subareas = list(curr_area["subareas"].values())
        subarea_targets += [s for s in subareas if len(s["subareas"]) > 0]

    while len(subarea_targets) > 0:
        curr_area = subarea_targets.pop(0)

        # Run context generation
        subareas = list(curr_area["subareas"].values())
        subarea_names = [s["name"] for s in subareas]
        entrance = determine_entrance(
            curr_area["name"],
            subarea_names,
            builder_config,
        )
        curr_area["neighbors"].append(curr_area["subareas"][entrance])
        curr_area["subareas"][entrance]["neighbors"].append(curr_area)

        # Add new subsubarea targets
        subarea_targets += [s for s in subareas if len(s["subareas"]) > 0]
    return area_map


# For each connection, provide both room descriptions and query for an edge in both directions
EDGE_TO_DIRECTION = """I'm writing a fantasy text adventure game. The following rooms are connected:
{} is connected to {}.

The description for {} is as follows:
{}

Provide a label for the path connecting {} to {}, as well as a description one would see examining that path from {}.

Label: <A sentence fragment noting the connection>
Description: <A sentence or two describing what one would see when looking at the connection>

The label should be able to be displayed in a list of possible routes, such as "an old doorway leading inwards", or "a dusty trail leading into the distance". Be descriptive!

Label:"""


@retry(count=7)
def create_connection(
    local_location: str,
    location_description: str,
    nearby_location: str,
    builder_config: "DictConfig",
) -> Tuple[str, str]:
    """Given a location, provide the description and backstory"""
    final_prompt = EDGE_TO_DIRECTION.format(
        local_location,
        nearby_location,
        local_location,
        location_description,
        local_location,
        nearby_location,
        local_location,
    )
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = result.strip()
    label, desc = result.split("\nDescription:")
    label = label[0].lower() + label[1:]
    return (clean_strip(label), desc.strip())


def fill_edge_information(
    area_map: Dict[str, Area],
    builder_config: "DictConfig",
) -> Dict[str, Area]:
    """For every neighbor in the map, produce edges"""
    main_areas = list(area_map.values())
    all_subareas = []  # Only subareas, main areas don't have edges/neighbors
    for area in main_areas:
        all_subareas += area["subareas"].values()

    while len(all_subareas) > 0:
        curr_area = all_subareas.pop(0)

        if len(curr_area.get("edges", [])) > 0:
            continue  # edges already done here

        desc = curr_area["description"]
        name = curr_area["name"]
        if len(curr_area["subareas"]) > 0:
            name += " (outside)"
        neighbor_list = curr_area["neighbors"]

        edge_map = {}
        seen_edges = set()
        pending_neighbors = list(neighbor_list)
        max_fails = len(pending_neighbors)
        tries = 0
        while len(pending_neighbors) > 0:
            n = pending_neighbors.pop()
            n_name = n["name"]
            if len(n["subareas"]) > 0:
                n_name += " (outside)"
            edge_info = create_connection(name, desc, n_name, builder_config)
            if edge_info[0] in seen_edges:
                tries += 1
                if tries > max_fails:
                    # Fall back to generic if we keep failing
                    edge_list.append((f"a path to {n_name}", edge_info[1]))
                    continue
                else:
                    pending_neighbors.append(n)
                    continue
            seen_edges.add(edge_info[0])
            edge_map[n["name"]] = edge_info

        curr_area["edges"] = edge_map

        if len(curr_area["subareas"]) > 0:
            all_subareas += list(curr_area["subareas"].values())

    return area_map


# Determine the characters and items in each room
# This query can take a room description and produce the labelling of characters, locations, and objects
LOCATION_ANNOTATION = """Given setting context, a location name and description, label the characters, objects, and nearby locations *currently* present within the location according to the description. If none are in a category, write "- None"
Some rules for characters:
- Be creative, rather than listing groups, generate names for a few members like '<name> the villager' rather than 'villagers', choosing an actual name rather than using <name>.
- Come up with your own names, NEVER USE <name> anywhere in the list!
- Never number an entry like "warrior 3".
- Don't list characters just by their relationship (like "<name>'s husband"), but feel free to note relationships to other characters in parantheticals, like "<name> the baker (farmer <name>'s husband)".

Setting Context:
""
{}
""

Remember, never use <name> anywhere in the list!

Location name: {}
Description: {}
Characters:
- """


@retry(count=7)
def annotate_location(
    area_prompt: str,
    location_name: str,
    location_description: str,
    builder_config: "DictConfig",
) -> Dict[str, List[str]]:
    """Given a location and description, provide contents"""
    final_prompt = LOCATION_ANNOTATION.format(
        area_prompt, location_name, location_description
    )
    if builder_config._backend == "openai":
        result = query_openai(final_prompt, temperature=0.6)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    assert "<name>" not in result.lower(), "Provided a template name <name>"

    characters, other = result.split("\nObjects:")
    objects = other.split("\nN")[0]
    return {
        "characters": [
            clean_strip(elem.strip("- ").strip().split(",")[0])
            for elem in characters.strip().split("\n")
            if elem.lower() != "- none"
        ],
        "objects": [
            clean_strip(elem.strip("- ").strip().split(",")[0].split(" - ")[0])
            for elem in objects.strip().split("\n")
            if elem != "- None"
        ],
    }


def annotate_all_locations(
    area_map: Dict[str, Area],
    builder_config: "DictConfig",
) -> Tuple[Dict[str, Area], List[str], List[str]]:
    """Provide annotatons for every location"""
    main_areas = list(area_map.values())
    all_subareas = []  # Only subareas, main areas don't have edges/neighbors
    for area in main_areas:
        all_subareas += area["subareas"].values()

    all_characters = []
    all_objects = []

    while len(all_subareas) > 0:
        curr_area = all_subareas.pop(0)

        if curr_area["processed"]:
            continue

        name = curr_area["name"]
        if len(curr_area["subareas"]) > 0:
            name += " (outside)"

        annotations = annotate_location(
            curr_area["backstory"],
            name,
            curr_area["description"],
            builder_config,
        )

        curr_area.update(annotations)
        all_characters += annotations["characters"]
        all_objects += annotations["objects"]

        if len(curr_area["subareas"]) > 0:
            all_subareas += list(curr_area["subareas"].values())
        curr_area["processed"] = True

    return area_map, all_characters, all_objects


# Deduplicate the total character + item list
DEDUPE_CHARACTERS = """​​I'm building out a text adventure game map, but want to deduplicate characters. Here is a list of all of the characters:

{}

We want to deduplicate this list. Please provide a version of the list after deduplicating. When two entries are similar, retain the earlier one.

Characters:
-"""
DEDUPE_ITEMS = """​​I'm building out a text adventure game map, but want to deduplicate objects. Here is a list of all of the objects:

{}

We want to deduplicate this list. Please provide a version of the list after deduplicating. When two entries are similar, retain the earlier one.

Objects:
-"""


@retry(count=7)
def deduplicate_list(
    items: List[str],
    builder_config: "DictConfig",
    is_obj: False,
) -> List[str]:
    """Deduplicate list from an area"""
    DEDUPE_PROMPT = DEDUPE_ITEMS if is_obj else DEDUPE_CHARACTERS
    item_list = "\n".join(["- " + a for a in items])

    final_prompt = DEDUPE_PROMPT.format(item_list)
    if builder_config._backend == "openai":
        result = "\n-" + query_openai(final_prompt, temperature=0.3)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    result = result.split("\n- ")[1:]
    for r in result:
        assert r in items, f"Item {r} returned not in {items}"

    # remove X the Y examples with different "Y"' for same Xs
    no_the_results = [r for r in result if " the " not in r]
    the_results = [r for r in result if " the " in r]
    the_leads = set()
    for tr in the_results:
        pre_the, post_the = tr.split(" the ", 1)
        if pre_the in no_the_results or pre_the in the_leads:
            continue
        no_the_results.append(tr)
        the_leads.add(pre_the)

    return no_the_results


# Populate the motivation and background for each of the characters that
# have been added, as well as carrying/holding
# This query can take a character and their relevant location and produce a relevant persona, description, and motivation, with wearing/wielding/carrying
ROOM_CHARACTER_ANNOTATION = """I'm writing a fantasy story with the following context:
""
{}
""

Given a medieval fantasy story setting description and a character name, provide the following details for the singular form of the character. Follow the provided template:
Setting: The setting to use as context
Character Name: The name of the character to provide answers on. May include paranthetical hints, these should be removed in the singular names.
Singular Form: singular form of the provided character, retaining titles and non-parenthetical details (removing capitalization unless a proper noun or name).
Singular Persona: A set of defining goal, characteristics, or backstory for this character, written in *first person* perspective.
Singular Physical Description: An appropriate physical description for the character in third person, such that it could be used in narration to someone not present.
Singular Motivation: A single goal relevant to what this character wants to achieve, written in first-person perspective.
Emoji: the most relevant emoji representing this specific character or their persona (like ⚔)
Carrying: Comma-separated list of objects this character is currently carrying, or None if the character isn't carrying anything.
Wielding: Comma-separated list of objects is currently wielding, or None if the character isn't wielding anything.
Wearing: Comma-separated list of objects is currently wearing, or None if the character isn't wearing anything.

Setting: {}
Character Name: {}
Singular Form:"""


@retry(count=10)
def annotate_set_character(
    story_plan: str,
    location_description: str,
    character_name: str,
    builder_config: "DictConfig",
) -> Dict[str, List[str]]:
    """Given a character and the room they come from, annotate attributes AND contents"""
    final_prompt = ROOM_CHARACTER_ANNOTATION.format(
        story_plan, location_description, character_name
    )
    if builder_config._backend == "openai":
        result = query_openai(final_prompt)
    else:
        raise AssertionError(f"Unsupported backend {builder_config._backend}")

    singular, other = result.split("\nSingular Persona:")
    persona, other = other.split("\nSingular Physical Description:")
    description, other = other.split("\nSingular Motivation:")
    motivation, other = other.split("\nEmoji:")
    emoji, other = other.split("\nCarrying:")
    carryings, other = other.split("\nWielding:")
    wieldings, wearings = other.split("\nWearing:")
    carry_list = [] if carryings.lower() == "none" else carryings.split(", ")
    wield_list = [] if wieldings.lower() == "none" else wieldings.split(", ")
    wear_list = [] if wearings.lower() == "none" else wearings.split(", ")
    singular, name_prefix = strip_articles(singular)
    if name_prefix is None:
        name_prefix = "an" if singular.lower()[0] in "aeiou" else "a"
        name_prefix = name_prefix if singular.lower() == singular else ""

    return {
        "singular": singular.strip().split(" (")[0],
        "plural": plural.strip(),
        "persona": persona.strip(),
        "description": description.strip(),
        "motivation": motivation.strip(),
        "emoji": emoji.strip(),
        "carrying": [c.strip() for c in carry_list if c.lower().strip() != "none"],
        "wielding": [
            c.strip()
            for c in wield_list
            if c.lower().strip() != "none" and c not in carry_list
        ],
        "wearing": [
            c.strip()
            for c in wear_list
            if c.lower().strip() != "none" and c not in carry_list
        ],
        "name_prefix": name_prefix,
    }


def generate_char_info(
    story_plan: str,
    area_map: Dict[str, Area],
    all_chars: List[str],
    builder_config: "DictConfig",
) -> Tuple[Dict[str, Area], int]:
    """
    Generates info for every character, and additionally returns the number of objects added
    while creating this information.
    """
    objs_added = 0
    all_char_set = set([c.lower() for c in all_chars])
    created_char_set = set()
    main_areas = list(area_map.values())
    all_subareas = []  # Only subareas, main areas aren't rooms
    for area in main_areas:
        all_subareas += area["subareas"].values()

    while len(all_subareas) > 0:
        curr_area = all_subareas.pop(0)

        if curr_area.get("processed_characters") is not None:
            continue

        characters = curr_area["characters"]
        processed_characters = []
        for c in characters:
            if c.lower() not in all_char_set:
                continue
            if c.lower() == "none":
                continue

            processed_char = annotate_set_character(
                story_plan,
                curr_area["description"],
                c,
                builder_config,
            )
            processed_char["name"] = c
            if processed_char["singular"].lower() in created_char_set:
                continue
            created_char_set.add(processed_char["singular"].lower())

            print(c.lower(), "->", processed_char["singular"])
            processed_characters.append(processed_char)
            all_char_set.remove(c.lower())
            objs_added += len(
                processed_char["carrying"]
                + processed_char["wielding"]
                + processed_char["wearing"]
            )

        curr_area["processed_characters"] = processed_characters

        if len(curr_area["subareas"]) > 0:
            all_subareas += list(curr_area["subareas"].values())
    return area_map, objs_added


# This query can take an object and their relevant character and provide a description and attributes
OBJECT_ANNOTATION = """I'm writing a text adventure with the following context:
""
{}
""

Given a an object name from a medieval fantasy text adventure, provide a physical description for the singular form, as well as values for the specific attributes below. For names, remove capitalization unless the name is a proper noun or specially named object. Also remove any parentheticals. For example:
Name: Swords (from the armory)
Singular form: sword
Plural form: swords
Singular description: This sword is sharp and heavy, and could likely do a lot of damage if swung. Don't swing it at anything important! It appears to be from the local armory.
Food: no
Drink: no
Holdable: yes
Wearable: no
Wieldable: yes
Surface: no
Container: no

Name:{}
Singular form:"""


@retry(count=10)
def annotate_object(
    base_prompt: str, object_name: str, builder_config: "DictConfig"
) -> Dict[str, List[str]]:
    """Given an object name, annotate it fully"""
    final_prompt = OBJECT_ANNOTATION.format(base_prompt, object_name)
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
    singular = singular.strip()
    name_prefix = "an" if singular.lower()[0] in "aeiou" else "a"
    name_prefix = name_prefix if singular.lower() == singular else "the"
    return {
        "singular": singular.strip(),
        "plural": plural.strip(),
        "description": description.strip(),
        "is_food": is_food.strip() == "yes",
        "is_drink": is_drink.strip() == "yes",
        "is_holdable": is_holdable.strip() == "yes",
        "is_wearable": is_wearable.strip() == "yes",
        "is_wieldable": is_wieldable.strip() == "yes",
        "is_surface": is_surface.strip() == "yes",
        "is_container": is_container.strip() == "yes",
        "name_prefix": name_prefix,
    }


def generate_obj_info(
    story_plan: str,
    area_map: Dict[str, Area],
    all_objs: List[str],
    builder_config: "DictConfig",
) -> Dict[str, Area]:
    """Generate object info for all objects in the scene"""
    all_obj_set = set(all_objs)
    main_areas = list(area_map.values())
    all_subareas = []  # Only subareas, main areas aren't rooms
    for area in main_areas:
        all_subareas += area["subareas"].values()

    while len(all_subareas) > 0:
        curr_area = all_subareas.pop(0)

        if len(curr_area["subareas"]) > 0:
            all_subareas += list(curr_area["subareas"].values())

        for c in curr_area["processed_characters"]:
            if c.get("processed_wearing") is not None:
                continue

            processed_carrying = []
            for o in c["carrying"]:
                processed_obj = annotate_object(
                    story_plan,
                    o,
                    builder_config,
                )
                processed_obj["name"] = o
                processed_carrying.append(processed_obj)
            c["processed_carrying"] = processed_carrying

            processed_wielding = []
            for o in c["wielding"]:
                processed_obj = annotate_object(
                    story_plan,
                    o,
                    builder_config,
                )
                processed_obj["name"] = o
                processed_wielding.append(processed_obj)
            c["processed_wielding"] = processed_wielding

            processed_wearing = []
            for o in c["wearing"]:
                processed_obj = annotate_object(
                    story_plan,
                    o,
                    builder_config,
                )
                processed_obj["name"] = o
                processed_wearing.append(processed_obj)
            c["processed_wearing"] = processed_wearing

        if curr_area.get("processed_objects") is not None:
            continue

        objects = curr_area["objects"]
        processed_objects = []
        for o in objects:
            if o not in all_obj_set:
                continue
            if o.lower() == "none":
                continue

            processed_obj = annotate_object(
                story_plan,
                o,
                builder_config,
            )
            processed_obj["name"] = o
            processed_objects.append(processed_obj)
            all_obj_set.remove(o)

        curr_area["processed_objects"] = processed_objects
    return area_map


class LLMPlannedGraphBuilder(GraphBuilder):
    """
    Builds a LIGHT world by first prompting a LLM for a rough plan and context,
    then prompting to convert that context into a graph
    """

    CONFIG_CLASS = LLMPromptBuilderConfig

    def __init__(self, builder_config: "DictConfig"):
        """Initialize the LLM"""
        self.builder_config = builder_config
        if builder_config._backend == "openai":
            openai.organization = builder_config.openai_org_id
            openai.api_key = builder_config.openai_secret_key
        else:
            raise AssertionError(f"Unsupported backend {builder_config._backend}")

        self.possible_agents: Dict[str, Dict[str, Any]] = {}  # char name to props

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
        self._add_character_objects(character, g)

        self._spawn_agent_in_room(world, agent_node, target_room)
        return agent_node

    def _add_object_list(
        self, obj_list: List[Dict[str, Any]], g: OOGraph, target_node: Any
    ) -> List[Any]:
        """Add the given list of objects to the graph, return the node list"""
        nodes = []
        objects = self._cleanup_names(obj_list)
        for obj in objects:
            object_node = g.add_object(
                obj["singular"],
                self._props_from_obj(obj),
            )
            object_node.force_move_to(target_node)
        return nodes

    def _add_character_objects(self, character: Dict[str, Any], g: OOGraph) -> None:
        """
        Add the objects from the given character to the graph,
        return the list of nodes added
        """
        carry_nodes = self._add_object_list(
            character["processed_carrying"], g, character["node"]
        )
        wield_nodes = self._add_object_list(
            character["processed_wielding"], g, character["node"]
        )
        for n in wield_nodes:
            n.equipped = "wield"
        wear_nodes = self._add_object_list(
            character["processed_wearing"], g, character["node"]
        )
        for n in wear_nodes:
            n.equipped = "wear"
        return carry_nodes + wield_nodes + wear_nodes

    def reset_graph(self) -> None:
        """Reset the current state of this builder before a rebuild"""
        self.possible_agents = {}  # char name to props

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
            if "name" in elem:
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

    def _count_areas(self, area_map: Dict[str, Area]) -> int:
        """Return a count of areas in the given map. May double-count shared"""
        return sum([self._count_areas(s["subareas"]) for s in area_map.values()]) + 1

    def _count_edges(self, area_map: Dict[str, Area]) -> int:
        """Return a count of edges in the given map. May double-count shared"""
        return sum(
            [
                self._count_edges(s["subareas"]) + len(s["neighbors"])
                for s in area_map.values()
            ]
        )

    def _count_characters(self, area_map: Dict[str, Area]) -> int:
        """Return a count of characters in the given map. May double-count shared"""
        return sum(
            [
                self._count_characters(s["subareas"]) + len(s.get("characters", []))
                for s in area_map.values()
            ]
        )

    def _count_objects(self, area_map: Dict[str, Area]) -> int:
        """
        Return a count of objects in the given map.
        May double-count shared, doesn't count held objects.
        """
        return sum(
            [
                self._count_objects(s["subareas"]) + len(s.get("objects", []))
                for s in area_map.values()
            ]
        )

    def _get_annotated_characters(
        self, area_map: Dict[str, Area]
    ) -> List[Dict[str, Any]]:
        """Extract processed characters across the map"""
        characters = []
        areas = area_map.values()
        for area in areas:
            characters += area.get("processed_characters", [])
            characters += self._get_annotated_characters(area["subareas"])
        return characters

    def _add_all_rooms(self, area_map: Dict[str, Area], g: OOGraph) -> List[Any]:
        """Add all of the rooms from the area_map to the graph"""
        nodes = []
        main_areas = list(area_map.values())
        all_subareas = []  # Only subareas, main areas aren't rooms
        for area in main_areas:
            all_subareas += area["subareas"].values()

        while len(all_subareas) > 0:
            curr_area = all_subareas.pop(0)

            if len(curr_area["subareas"]) > 0:
                all_subareas += list(curr_area["subareas"].values())

            if curr_area.get("node") is not None:
                continue  # already added

            room_node = g.add_room(
                curr_area["name"],
                {
                    "room": True,
                    "desc": curr_area["description"],
                    "extra_desc": curr_area["backstory"],
                    "size": 2000,
                    "contain_size": 2000,
                    "name_prefix": "the",
                    "surface_type": "in",
                    "classes": {"room"},
                },
            )
            curr_area["node"] = room_node
            nodes.append(room_node)

        # Attach the neighbors
        for area in main_areas:
            all_subareas += area["subareas"].values()

        while len(all_subareas) > 0:
            curr_area = all_subareas.pop(0)

            for n in curr_area["neighbors"]:
                label, desc = curr_area["edges"][n["name"]]
                curr_area["node"].add_neighbor(n["node"], label, None, desc)

            if len(curr_area["subareas"]) > 0:
                all_subareas += list(curr_area["subareas"].values())

        return nodes

    def _add_all_chars(self, area_map: Dict[str, Area], g: OOGraph) -> List[Any]:
        """Add all characters in the given map to the provided graph, return nodes added"""
        nodes = []
        main_areas = list(area_map.values())
        all_subareas = []  # Only subareas, main areas aren't rooms
        for area in main_areas:
            all_subareas += area["subareas"].values()

        while len(all_subareas) > 0:
            curr_area = all_subareas.pop(0)
            if curr_area.get("chars_added") is True:
                continue

            if len(curr_area["subareas"]) > 0:
                all_subareas += list(curr_area["subareas"].values())

            characters = self._cleanup_names(curr_area["processed_characters"])

            for target_char in characters:
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
                        "emoji": target_char["emoji"],
                    },
                )
                target_char["node"] = agent_node
                agent_node.move_to(curr_area["node"])
                nodes.append(agent_node)
            curr_area["chars_added"] = True

        return nodes

    def _add_all_objs(self, area_map: Dict[str, Area], g: OOGraph) -> List[Any]:
        nodes = []
        main_areas = list(area_map.values())
        all_subareas = []  # Only subareas, main areas aren't rooms
        for area in main_areas:
            all_subareas += area["subareas"].values()

        while len(all_subareas) > 0:
            curr_area = all_subareas.pop(0)
            if curr_area.get("objs_added") is True:
                continue

            # add character objects
            for char in curr_area["processed_characters"]:
                nodes += self._add_character_objects(char, g)

            objects = self._cleanup_names(curr_area["processed_objects"])
            for obj in objects:
                object_node = g.add_object(
                    obj["singular"],
                    self._props_from_obj(obj),
                )
                object_node.move_to(curr_area["node"])
                nodes.append(object_node)

            if len(curr_area["subareas"]) > 0:
                all_subareas += list(curr_area["subareas"].values())

            curr_area["objs_added"] = True

        return nodes

    def build_graph(self, prompt: str) -> OOGraph:
        """Build a graph from the given prompt"""
        self.reset_graph()

        # First get a plan
        print("Generating story summary:")
        story_plan = create_plan_from_prompt(prompt, self.builder_config)

        # Then create the initial areas
        print("\nConverting to initial area list")
        first_areas = get_areas_from_plan(story_plan, self.builder_config)
        print(f" {len(first_areas)} Initial areas created.")

        # Get first area pass, sublocations for each area
        print("Generating full area list")
        raw_area_dict = get_area_room_map_from_plan(
            story_plan, first_areas, self.builder_config
        )
        area_count = sum([len(x) for x in raw_area_dict.values()])
        area_map = room_map_to_areas(raw_area_dict)
        print(f" {area_count} total areas created.")

        # Handle sublocating main areas that are really sublocations
        print("Maybe sublocating main areas")
        subarea_mapping = get_subarea_mapping(
            story_plan, first_areas, self.builder_config
        )
        area_map = apply_subarea_mapping(area_map, subarea_mapping)
        print(f" {len(area_map)} top-level areas remain.")

        # Get links between remaining main areas
        print("Linking top-level main areas")
        area_link = link_main_areas(
            story_plan, list(area_map.keys()), self.builder_config
        )
        area_map = add_links(area_map, area_link)
        link_count = len([c for c in area_link.values() if c is not None])
        print(f" {link_count} top-level links created.")

        # Deduplicate areas
        print("Deduplicating map areas that are too similar")
        area_count_pre = self._count_areas(area_map)
        area_map = deduplicate_all_main_areas(area_map, self.builder_config)
        area_count = self._count_areas(area_map)
        print(f" {area_count_pre - area_count} areas removed.")

        # Apply subarea mapping to subareas now
        print("Running subarea mapping for subareas")
        area_map = run_subsubarea_mapping(story_plan, area_map, self.builder_config)
        print(" done.")

        # Create plans for areas containing subareas
        print("Getting context for area groups")
        area_map = describe_all_main_areas(story_plan, area_map, self.builder_config)
        print(" done.")

        # Determine routing within subareas
        print("Running linking within subareas")
        area_map = run_subarea_neighboring(story_plan, area_map, self.builder_config)
        edge_count = self._count_edges(area_map)
        print(f" {edge_count} edges noted")

        # Create descriptions for all areas
        print(f"Creating context for {area_count} areas")
        area_map = describe_all_locations(story_plan, area_map, self.builder_config)
        print(" done.")

        # Determine the correct "main" location for container locations
        print("Determining entrance for container locations")
        edge_count_before = edge_count
        area_map = mark_all_entrances(area_map, self.builder_config)
        edge_count = self._count_edges(area_map)
        print(f" {edge_count - edge_count_before} edges added.")

        # Determine the label and description for all edges
        print(f"Labelling all {edge_count} edges")
        area_map = fill_edge_information(area_map, self.builder_config)
        print(" done.")

        # Annotate location contents
        print(f"Annotating contents for all {area_count} locations.")
        area_map, all_chars, all_objs = annotate_all_locations(
            area_map, self.builder_config
        )
        object_count = self._count_objects(area_map)
        character_count = self._count_characters(area_map)
        print(f" {object_count} objects and {character_count} characters added.")

        # Create deduplication lists
        print("Deduplicating objects and characters")
        dedup_objs = deduplicate_list(all_objs, self.builder_config, is_obj=True)
        dedup_chars = deduplicate_list(all_chars, self.builder_config, is_obj=False)
        objs_removed = object_count - len(dedup_objs)
        chars_removed = character_count - len(dedup_chars)
        print(f" {objs_removed} objects removed, {chars_removed} characters removed.")

        # Annotate Characters
        print("Annotating all characters")
        area_map, new_objs = generate_char_info(
            story_plan, area_map, dedup_chars, self.builder_config
        )
        print(f" added {new_objs} objects while annotating characters.")

        # Annotate Objects
        print(f"Annotating all {len(dedup_objs) + new_objs} objects")
        area_map = generate_obj_info(
            story_plan, area_map, dedup_objs, self.builder_config
        )
        print(" done.")

        print("Building graph from plan")
        g = OOGraph(title=prompt)
        rooms = self._add_all_rooms(area_map, g)
        agents = self._add_all_chars(area_map, g)
        objs = self._add_all_objs(area_map, g)
        print(
            f"Graph with {len(rooms)} rooms, {len(agents)} agents, and {len(objs)} objects created!"
        )

        try:
            self.possible_agents = self._get_annotated_characters(area_map)
        except Exception as e:
            print("Possible agent creation failed with exception")
            import traceback

            traceback.print_exc()
        return g

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

        builder = LLMPlannedGraphBuilder(config)
        graph = builder.build_graph(prompt)

        output_name = input("\nProvide output name:\n>") + ".json"
        output_dir = os.path.join(map_dir, output_name)
        with open(output_dir, "w+") as json_file:
            json_file.write(graph.to_json())
        print(f"Written to {output_dir}")
    print("Bye!")
