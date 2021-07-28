const Copy ={
    objects:{
        booleanAttributes:[
            "container",
            "surface",
            "living",
            "wieldable",
            "wearable",
        ],
        traits:[
            {
                name: "SIZE",
                description:"The physical size of an object",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Nail",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Sword",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Wagon",
                    color:"red"
                    }
                ]
            },
            {
                name: "VALUE",
                description:"The monetary value of an object.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Rock",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Silver Piece",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Treasure",
                    color:"red"
                    }
                ]
            },
            {
                name: "CONTAINER SIZE",
                description:"The space available inside container for storage.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Locket",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Satchel",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Shipping Crate",
                    color:"red"
                    }
                ]
            },
            {
                name: "WEAPON DAMAGE",
                description:"The base damage a weapon does when wielded agaisnt a foe.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Stick",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Sword",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Ballista",
                    color:"red"
                    }
                ]
            },
            {
                name: "ARMOR RATING",
                description:"The amount of protection a wearable object offers",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Shirt",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Leather Vest",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Platemail",
                    color:"red"
                    }
                ]
            },
            {
                name: "REFRESHMENT",
                description:"How refreshing an object is when consumed.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Millet",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Bread",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A feast",
                    color:"red"
                    }
                ]
            },
            {
                name: "WEIGHT",
                description:"The heaviness of an object.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Feather",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Pile of wood",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A Large Boulder",
                    color:"red"
                    }
                ]
            },
            {
                name: "RARITY",
                description:"How common the object is in the world.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A rock",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Iron",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Excalibur",
                    color:"red"
                    }
                ]
            },
        ]
        },
    characters:{
        booleanAttributes:[
            "arm and leg counts",
        ],
        traits:[
            {
                name: "STRENGTH",
                description:"The raw physical power an actor can exert typically fort he express purpose of attacking.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Rat",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Peasant",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Dragon",
                    color:"red"
                    }
                ]
            },
            {
                name: "CONSTITUTION",
                description:"The physical toughness and ability to take damage possessed by an actor",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Butterfly",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Peasant",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Stone Golem",
                    color:"red"
                    }
                ]
            },
            {
                name: "CHARISMA",
                description:"",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Gelatinous Cube",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Bard",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Dryad",
                    color:"red"
                    }
                ]
            },
            {
                name: "DEXTERITY",
                description:"The speed, skill, and agility of an actor.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Living Statue",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Peasant",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Legendary Thief",
                    color:"red"
                    }
                ]
            },
            {
                name: "INTELLIGENCE",
                description:"The ability of an actor to learn and retain knowledge both magical and practical.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "A Stump",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Student",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Wizard Prodigy",
                    color:"red"
                    }
                ]
            },
            {
                name: "WISDOM",
                description:"An actor's willpower to make good decisions and experience to know what decisions are good.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Wildboar",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Peasant",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Ancient Sage",
                    color:"red"
                    }
                ]
            },
            {
                name: "SIZE",
                description:"The physical size of an actor",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "An Ant",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Human",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A Giant",
                    color:"red"
                    }
                ]
            },
            {
                name: "RARITY",
                description:"How common the actor is in the world.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Peasant",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Knight",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Royalty",
                    color:"red"
                    }
                ]
            },
        ]
      },
      locations:{
        booleanAttributes:[
            "indoors",
            "outdoors"
        ],
        traits:[
            {
                name: "SIZE",
                description:"The size of a location.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Hut",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Field",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Castle",
                    color:"red"
                    }
                ]
            },
            {
                name: "BRIGHTNESS",
                description:"The natural light and visibility of a location.",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Cave",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Candlelit Home",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "A Field at Noon",
                    color:"red"
                    }
                ]
            },
            {
                name: "TEMPERATURE",
                description:"The room temperature of a location",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Ice Cave",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Meadow",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Lava Cave",
                    color:"red"
                    }
                ]
            },
            {
                name: "RARITY",
                description:"The rarity of a location",
                scaleRange:[
                    {
                    name:"MIN",
                    example: "Field",
                    color:"green"
                    },
                    {
                    name:"MID",
                    example: "Village",
                    color:"blue"
                    },
                    {
                    name:"MAX",
                    example: "Secret Room",
                    color:"red"
                    }
                ]
            },
        ]
      },
      input:{
        defaultBooleanAttributes:[
        ],
        defaultScaleRange:[
            {
            name:"MIN",
            example: "Min",
            color:"green"
            },
            {
            name:"MID",
            example: "Mid",
            color:"blue"
            },
            {
            name:"MAX",
            example: "Max",
            color:"red"
            }
        ]
      },
}

export default Copy;
