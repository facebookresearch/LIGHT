#!/usr/bin/env python3
import random


class FillerRoom(object):
    """An Object Oriented Abstraction of a filler room. 
    Implemented in similar manner as DBRoom"""

    def __init__(self, category=None, name=None, description=None, background=None):
        self.category = category
        self.setting = name
        self.description = description
        self.background = background
        self.in_characters = []
        self.ex_characters = []
        self.in_objects = []
        self.ex_objects = []
        self.neighbors = []
        self.ind = 1  # FIXME
        if name is not None:
            self.db_id = name
        else:
            self.db_id = "filler_room"
        self.g_id = None
        self.loc = None
        self.possible_connections = {}


def to_legacy_dict(filler_room):
    """Takes in a filler_room object and return a dict 
    representation that reflects the legacy implementation of the filler room"""
    filler_room_dict = {}
    filler_room_dict["category"] = filler_room.category
    filler_room_dict["setting"] = filler_room.setting
    filler_room_dict["description"] = filler_room.description
    filler_room_dict["background"] = filler_room.background
    filler_room_dict["in_characters"] = filler_room.in_characters
    filler_room_dict["ex_characters"] = filler_room.ex_characters
    filler_room_dict["in_objects"] = filler_room.in_objects
    filler_room_dict["ex_objects"] = filler_room.ex_objects
    filler_room_dict["neighbors"] = filler_room.neighbors
    filler_room_dict["ind"] = filler_room.ind
    filler_room_dict["db_id"] = filler_room.db_id
    filler_room_dict["g_id"] = filler_room.g_id
    filler_room_dict["loc"] = filler_room.loc
    filler_room_dict["possible_connections"] = filler_room.possible_connections
    return filler_room_dict


def build_filler_rooms(db):
    category_set = []
    for room in db["rooms"]:
        category_set.append(db["rooms"][room]["category"])
    category_set = set(category_set)
    filler_rooms, categories = build_filler_rooms_from_categories(category_set)
    room_dicts = {
        categories: list(map(lambda r: to_legacy_dict(r), rooms))
        for categories, rooms in filler_rooms.items()
    }
    return room_dicts, categories


def build_filler_rooms_from_categories(category_set):
    d = {}
    cannot_link_out = set(
        ["Empty storage room", "Dusty closet"]
    )  # FIXME some rooms shouldn't have exits
    indoor = ["Hallway", "Empty storage room", "Dusty closet", "Unused chamber"]
    outdoor = [
        "Meadow",
        "Field",
        "Stretch of road",
        "Sandy beach",
        "Trail",
        "Small cave",
        "Little clearing",
        "Abandoned farm",
        "Old shack",
    ]
    outdoor_town = [
        "Stretch of road",
        "Trail",
        "Small glen",
        "Cobblestone path",
        "Central garden",
        "Town garden",
    ]
    wilderness = ["Abandoned hut", "Old campsite", "Run down path", "Trail"]
    characteristics = ["grass", "water", "dirt", "gravel", "dust"]
    obstacles = [
        "hard to cross",
        "completely empty",
        "like no one has been here in awhile",
    ]

    d["Graveyard"] = outdoor
    d["Countryside"] = outdoor
    d["Bazaar"] = outdoor_town
    d["Outside Castle"] = outdoor
    d["Forest"] = wilderness
    d["Desert"] = wilderness
    d["Jungle"] = wilderness
    d["Outside Church"] = outdoor_town
    d["Port"] = outdoor_town
    d["Lake"] = wilderness
    d["Outside Palace"] = outdoor_town
    d["Abandoned"] = wilderness
    d["Shore"] = wilderness
    d["Wasteland"] = wilderness
    d["Outside Tower"] = outdoor
    d["Mountain"] = wilderness
    d["Town"] = outdoor_town
    d["Cave"] = wilderness
    d["Trail"] = outdoor
    d["Outside Cottage"] = outdoor_town
    d["Farm"] = outdoor
    d["Outside Temple"] = outdoor_town
    d["Swamp"] = wilderness

    for cat in category_set:
        if cat not in d:
            d[cat] = indoor

    pluggable_descriptions = [
        "There isn't much here.",
        "Maybe there is somewhere else more interesting.",
        "Maybe you should go look somewhere else.",
        "It doesn't look interesting here.",
        "The area looks pretty empty.",
        "This is a [FILL], but it looks [OBSTACLE].",
        "This is a dirty [FILL].",
        "This is an old [FILL].",
        "This is a run down [FILL], it looks [OBSTACLE].",
        "There's a bit of [CHARACTERISTIC].",
    ]
    background = [
        "Sometimes things are just what they seem. There's nothing interesting here."
    ]

    filler_rooms = {}
    filler_room_names = []
    for category in d:
        filler_rooms[category] = []
        for name in d[category]:
            for description in pluggable_descriptions:
                filler_room_names.append(name.lower())
                if "[FILL]" in description:
                    description = description.replace(
                        "[FILL]", name.split()[-1].lower()
                    )
                if "[OBSTACLE]" in description:
                    description = description.replace(
                        "[OBSTACLE]", random.choice(obstacles)
                    )
                if "[CHARACTERISTIC]" in description:
                    description = description.replace(
                        "[CHARACTERISTIC]", random.choice(characteristics)
                    )
            build_room = FillerRoom(category, name, description, background)
            filler_rooms[category].append(build_room)
    return filler_rooms, set(filler_room_names)
