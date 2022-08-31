
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// const DummyWorlds = [
//     {
//         id:0, 
//         name: "Mars", 
//         tags:["#red", "#haunted", "#dry"],
//         rooms: [
//             {
//                 id:0, 
//                 name: "Dungeon", 
//                 description:"A dark, cold prison.",
//                 objects: [
//                     {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
//                     {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
//                     {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
//                   ],
//                 characters: [
//                     {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
//                     {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
//                     {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
//                 ]
//             },
//             {
//                 id:1, 
//                 name: "Forest", 
//                 description:"A wild maze of trees.",
//                 objects: [
//                     {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
//                     {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
//                     {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
//                   ],
//                 characters: [
//                     {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
//                     {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
//                     {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
//                 ]
//             },
//             {
//                 id:2, 
//                 name: "Village", 
//                 description:"A quiet village.",
//                 objects: [
//                     {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
//                     {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
//                     {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
//                   ],
//                 characters:[
//                     {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
//                     {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
//                     {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
//                 ]
//             }
//         ]
//     },
//     {
//         id:1, 
//         name: "Norrath", 
//         tags:["#magical", "#amazing", "#dragons"],
//         rooms: [
//             {
//                 id:0, 
//                 name: "Dungeon", 
//                 description:"A dark, cold prison.",
//                 objects: [
//                     {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
//                     {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
//                     {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
//                   ],
//                 characters: [
//                     {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
//                     {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
//                     {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
//                 ]
//             },
//             {
//                 id:1, 
//                 name: "Forest", 
//                 description:"A wild maze of trees.",
//                 objects: [
//                     {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
//                     {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
//                     {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
//                   ],
//                 characters: [
//                     {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
//                     {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
//                     {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
//                 ]
//             },
//             {
//                 id:2, 
//                 name: "Village", 
//                 description:"A quiet village.",
//                 objects: [
//                     {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
//                     {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
//                     {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
//                   ],
//                 characters:[
//                     {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
//                     {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
//                     {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
//                 ]
//             }
//         ]
//     }, 
//     {
//         id:2, 
//         name:"Asgard", 
//         tags:["#vikings", "#gods", "#magic"],
//         rooms: [
//             {
//                 id:0, 
//                 name: "Dungeon", 
//                 description:"A dark, cold prison.",
//                 objects: [
//                     {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
//                     {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
//                     {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
//                   ],
//                 characters: [
//                     {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
//                     {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
//                     {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
//                 ]
//             },
//             {
//                 id:1, 
//                 name: "Forest", 
//                 description:"A wild maze of trees.",
//                 objects: [
//                     {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
//                     {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
//                     {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
//                   ],
//                 characters: [
//                     {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
//                     {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
//                     {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
//                 ]
//             },
//             {
//                 id:2, 
//                 name: "Village", 
//                 description:"A quiet village.",
//                 objects: [
//                     {id:0, name: "A bone club", description:"A crude weapon made from a large bone."},
//                     {id:1, name: "A plate helmet", description:"A shiny piece of armor for one's head."},
//                     {id:2, name: "A bucket", description:"An empty vessel that could be used to carry any number of things."}
//                   ],
//                 characters:[
//                     {id:0, name: "Orky the Orc", description:"Smarter than your average orc."},
//                     {id:1, name: "Gobbles the Goblin", description:"A hungry, hungry goblin."},
//                     {id:2, name: "Hugh Mann", description:"Just a regular peasant trying to get by."}
//                 ]
//             }
//         ]
//     }
// ]

//BASIC WORLD WITH A SMALL NUMBER OF NODES
const SimpleWorld = {
    id:1,
    name: "Simple World",
    tags:["#red", "#haunted", "#dry"],
    agents: ["kitty_3_5", "orc_2_4"],
    nodes: {
      church_entryway_1_2: {
        agent: false,
        classes: ["room"],
        contain_size: 100000,
        contained_nodes: {
          kitty_3_5: {
            target_id: "kitty_3_5"
          },
          muddy_area_6_7: {
            target_id: "muddy area_6_7"
          },
          scroll_9_1: {
            target_id: "scroll_9_1"
          },
          scroll_9_2: {
            target_id: "scroll_9_2"
          },
          scroll_9_3: {
            target_id: "scroll_9_3"
          },
          shovel_5_6: {
            target_id: "shovel_5_6"
          }
        },
        container_node: {
          target_id: "VOID"
        },
        db_id: null,
        desc: "The church has marble floors and a huge frost window. There are benches made from wood and a big organ can be seen at the front stage. There is gold trim all around the church.",
        extra_desc: "The church has marble floors and a huge frost window. There are benches made from wood and a big organ can be seen at the front stage. There is gold trim all around the church.",
        name: "Church Entryway",
        name_prefix: "the",
        names: ["Church Entryway"],
        neighbors: {
          orc_cave_0_1: {
            examine_desc: "You see a path!",
            label: "path to the west",
            locked_edge: null,
            target_id: "orc cave_0_1"
          }
        },
        node_id: "church entryway_1_2",
        object: false,
        room: true,
        size: 1,
        grid_location: [0, 0, 0],
        surface_type: "in"
      },
      kitty_3_5: {
        agent: true,
        aggression: 0,
        pacifist: false,
        char_type: "creature",
        classes: ["agent"],
        contain_size: 20,
        contained_nodes: {},
        container_node: {
          target_id: "church entryway_1_2"
        },
        damage: 1,
        db_id: null,
        defense: 0,
        desc: "Black and white and cute all over.",
        followed_by: {},
        following: null,
        food_energy: 1,
        health: 5,
        is_player: false,
        name: "kitty",
        name_prefix: "a",
        names: ["kitty"],
        tags: ["orc"],
        node_id: "kitty_3_5",
        object: false,
        on_events: null,
        persona: "I'm a cute kitty.",
        room: false,
        size: 20,
        speed: 20
      },
      muddy_area_6_7: {
        agent: false,
        classes: ["object"],
        contain_size: 20,
        contained_nodes: {},
        container: true,
        container_node: {
          target_id: "church entryway_1_2"
        },
        db_id: null,
        dead: false,
        desc: "A muddy area.",
        drink: false,
        equipped: null,
        food: false,
        food_energy: 0,
        gettable: false,
        locked_edge: null,
        name: "muddy area",
        name_prefix: "a",
        names: ["muddy area"],
        node_id: "muddy area_6_7",
        object: true,
        on_use: null,
        room: false,
        size: 1,
        stats: {
          damage: 0,
          defense: 0
        },
        surface_type: "in",
        value: 1,
        wearable: false,
        wieldable: false
      },
      orc_cave_0_1: {
        agent: false,
        classes: ["room"],
        contain_size: 100000,
        contained_nodes: {
          orc_2_4: {
            target_id: "orc_2_4"
          }
        },
        container_node: {
          target_id: "VOID"
        },
        db_id: null,
        desc: "It is a dark cave that is cold and damp inside. The floor is rocks covered in bat poop. It is damp from the ceiling dripping of water. The cave just goes on what seems to be endlessly into the dark abyss. The only light you can see is from the distance entrance of the cave.",
        extra_desc: "It is a dark cave that is cold and damp inside. The floor is rocks covered in bat poop. It is damp from the ceiling dripping of water. The cave just goes on what seems to be endlessly into the dark abyss. The only light you can see is from the distance entrance of the cave.",
        name: "Orc cave",
        name_prefix: "the",
        names: ["Orc cave"],
        neighbors: {
          church_entryway_1_2: {
            examine_desc: "You see a path!",
            label: "path to the east",
            locked_edge: null,
            target_id: "church entryway_1_2"
          }
        },
        node_id: "orc cave_0_1",
        object: false,
        room: true,
        size: 1,
        grid_location: [1, 0, 0],
        surface_type: "in"
      },
      orc_2_4: {
        agent: true,
        usually_npc: true,
        aggression: 0,
        char_type: "creature",
        classes: ["agent"],
        contain_size: 20,
        contained_nodes: {
          priceless_piece_of_art_4_3: {
            target_id: "priceless piece of art_4_3"
          }
        },
        container_node: {
          target_id: "orc cave_0_1"
        },
        damage: 1,
        db_id: null,
        defense: 0,
        desc: "You really don't have a good reason to be examining this orc closer.",
        followed_by: {},
        following: null,
        food_energy: 1,
        health: 10,
        is_player: false,
        name: "orc",
        name_prefix: "an",
        names: ["orc"],
        node_id: "orc_2_4",
        object: false,
        tags: ["orc"],
        attack_tagged_agents: ["!orc"],
        dont_accept_gifts: false,
        on_events: [
          [
            ["SayEvent", "lotr"],
            ["SayEvent", "One does not simply mention lotr!"]
          ],
          [
            ["SayEvent", "art"],
            [
              "SayEvent",
              "I might give you this piece of art if you give me something shiny for it."
            ]
          ],
          [
            ["SayEvent", "smile at me"],
            ["EmoteEvent", "smile"]
          ],
          [
            ["GiveObjectEvent", "ring"],
            ["GiveObjectEvent", "art", "other_agent"]
          ]
        ],
        persona: "I am a orc that was born in a cave. I eat corn the most. I have many friends.",
        room: false,
        size: 20,
        speed: 20
      },
      priceless_piece_of_art_4_3: {
        agent: false,
        classes: ["object"],
        contain_size: 0,
        contained_nodes: {},
        container: false,
        container_node: {
          target_id: "orc_2_4"
        },
        db_id: null,
        dead: false,
        desc: "A work of art that is has more than monetary value. Mostly owned by kings and wealthy collectors",
        drink: false,
        equipped: null,
        food: false,
        food_energy: 0,
        gettable: true,
        locked_edge: null,
        name: "priceless piece of art",
        name_prefix: "a",
        names: ["priceless piece of art"],
        node_id: "priceless piece of art_4_3",
        object: true,
        on_use: null,
        room: false,
        size: 1,
        stats: {
          damage: 0,
          defense: 0
        },
        surface_type: "on",
        value: 10,
        wearable: false,
        wieldable: true
      },
      shovel_5_6: {
        agent: false,
        classes: ["object"],
        contain_size: 0,
        contained_nodes: {},
        container: false,
        container_node: {
          target_id: "church entryway_1_2"
        },
        db_id: null,
        dead: false,
        desc: "A shovel",
        drink: false,
        equipped: null,
        food: false,
        food_energy: 0,
        gettable: true,
        locked_edge: null,
        name: "shovel",
        name_prefix: "a",
        names: ["shovel"],
        node_id: "shovel_5_6",
        object: true,
        on_use: [
            {
            remaining_uses: 1,
            events: [
              {
                type: "create_entity",
                params: {
                  type: "in_used_target_item",
                  object: {
                    name_prefix: "an",
                    is_wearable: true,
                    name: "emerald ring",
                    desc: "A beautiful and mysterious ring.. could it have magical powers?"
                  }
                }
              },
              {
                type: "broadcast_message",
                params: {
                  self_view: "You dig into the sodden mud, and spy something glistening within!"
                }
              }
            ],
            constraints: [
              {
                type: "is_holding",
                params: {
                  complement: "used_item"
                }
              },
              {
                type: "used_with_item_name",
                params: {
                  item: "muddy area"
                }
              }
            ]
          }
        ],
        room: false,
        size: 1,
        stats: {
          damage: 1,
          defense: 0
        },
        surface_type: "on",
        value: 1,
        wearable: false,
        wieldable: true
      },
      scroll_9_1: {
        agent: false,
        desc: "An old scroll with words you decipher to be: \"facere mortem\". Could this be magic?",
        name: "mortem scroll",
        drink: false,
        equipped: null,
        food: true,
        food_energy: 2,
        name_prefix: "a",
        value: 10,	
        node_id: "scroll_9_1",
        container_node: { 
            target_id: "church entryway_1_2" 
        },
        contained_nodes: {},
      object: true,
        on_use: [
          {
            events: [
              {
                type: "broadcast_message",
                params: {
                  self_view: "You say the words aloud, and runes on the scroll glow with gold.",
                  self_as_target_view: "You are struck with searing pain!",
                  self_not_target_view: "{recipient_text} is struck with searing pain!",
                  room_view: "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} is struck with searing pain!"
                }
              },
              {
                type: "modify_attribute",
                params: {
                  type: "in_used_target_item",
                  key: "health",
                  value: "-20"
                }
              }
            ],
            constraints: [
              {
                type: "is_holding",
                params: {
                  complement: "used_item"
                }
              },
              {
                type: "used_with_agent"
              }
            ]
          }
        ]
      },
      scroll_9_2: {
        agent: false,
        classes: ["object"],
        desc: "An old scroll with words you decipher to be: \"creo magnitudo\". Could this be magic?",
        name: "magnitudo scroll",
        name_prefix: "a",
        node_id: "scroll_9_2",
        container_node: { "target_id": "church entryway_1_2" },
        contained_nodes: {},
        object: true,
        on_use: [
          {
            events: [
              {
                type: "broadcast_message",
                params: {
                  self_view: "You say the words aloud, and runes on the scroll glow with gold.",
                  self_as_target_view: "Suddenly you feel a voluminous about you and you feel ... LARGER! You are  growing!",
                  self_not_target_view: "{recipient_text} appears to be growing larger!!!",
                  room_view: "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} seems to glow for a second.. and appears to be getting larger!"
                }
              },
              {
                type: "modify_attribute",
                params: {
                  type: "in_used_target_item",
                  key: "size",
                  value: "+2"
                }
              }
            ],
            constraints: [
              {
                type: "is_holding",
                params: {
                  complement: "used_item"
                }
              },
              {
                type: "used_with_agent"
              }
            ]
          }
        ]
      },
      scroll_9_3: {
        agent: false,
        classes: ["object"],
        desc: "An old scroll with words you decipher to be: \"creo dexteritate\". Could this be magic?",
        name: "dexteritate scroll",
        name_prefix: "a",
        node_id: "scroll_9_3",
        container_node: { "target_id": "church entryway_1_2" },
        contained_nodes: {},
        object: true,
        on_use: [
          {
            events: [
              {
                type: "broadcast_message",
                params: {
                  self_view: "You say the words aloud, and runes on the scroll glow with gold.",
                  self_as_target_view: "Suddenly you feel a lightness upon you and you feel more fleet of foot. Your dexterity has increased!",
                  self_not_target_view: "{recipient_text} feels a lightness upon them and they feel more fleet of foot. Their dexterity has increased!",
                  room_view: "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} seems to glow for a second."
                }
              },
              {
                type: "modify_attribute",
                params: {
                  type: "in_used_target_item",
                  key: "dexterity",
                  value: "+2"
                }
              }
            ],
            constraints: [
              {
                type: "is_holding",
                params: {
                  complement: "used_item"
                }
              },
              {
                type: "used_with_agent"
              }
            ]
          }
        ]
      }
    },
    objects: [
      "muddy area_6_7",
      "priceless piece of art_4_3",
      "shovel_5_6",
      "scroll_9_1",
      "scroll_9_2",
      "scroll_9_3"
    ],
    rooms: ["church entryway_1_2", "orc cave_0_1"]
}



//BASIC WORLD WITH A SMALL NUMBER OF NODES 2
const SimpleWorld2 = {
    id:2,
    name: "Simple World 2",
    agents: ["kitty_3_5", "orc_2_4"],
    tags:["#red", "#haunted", "#dry"],
    nodes: {
      church_entryway_1_2: {
        agent: false,
        classes: ["room"],
        contain_size: 100000,
        contained_nodes: {
          kitty_3_5: {
            target_id: "kitty_3_5"
          },
          muddy_area_6_7: {
            target_id: "muddy area_6_7"
          },
          scroll_9_1: {
            target_id: "scroll_9_1"
          },
          scroll_9_2: {
            target_id: "scroll_9_2"
          },
          scroll_9_3: {
            target_id: "scroll_9_3"
          },
          shovel_5_6: {
            target_id: "shovel_5_6"
          }
        },
        container_node: {
          target_id: "VOID"
        },
        db_id: null,
        desc: "The church has marble floors and a huge frost window. There are benches made from wood and a big organ can be seen at the front stage. There is gold trim all around the church.",
        extra_desc: "The church has marble floors and a huge frost window. There are benches made from wood and a big organ can be seen at the front stage. There is gold trim all around the church.",
        name: "Church Entryway",
        name_prefix: "the",
        names: ["Church Entryway"],
        neighbors: {
          orc_cave_0_1: {
            examine_desc: "You see a path!",
            label: "path to the west",
            locked_edge: null,
            target_id: "orc cave_0_1"
          }
        },
        node_id: "church entryway_1_2",
        object: false,
        room: true,
        size: 1,
        grid_location: [0, 0, 0],
        surface_type: "in"
      },
      kitty_3_5: {
        agent: true,
        aggression: 0,
        pacifist: false,
        char_type: "creature",
        classes: ["agent"],
        contain_size: 20,
        contained_nodes: {},
        container_node: {
          target_id: "church entryway_1_2"
        },
        damage: 1,
        db_id: null,
        defense: 0,
        desc: "Black and white and cute all over.",
        followed_by: {},
        following: null,
        food_energy: 1,
        health: 5,
        is_player: false,
        name: "kitty",
        name_prefix: "a",
        names: ["kitty"],
        tags: ["orc"],
        node_id: "kitty_3_5",
        object: false,
        on_events: null,
        persona: "I'm a cute kitty.",
        room: false,
        size: 20,
        speed: 20
      },
      muddy_area_6_7: {
        agent: false,
        classes: ["object"],
        contain_size: 20,
        contained_nodes: {},
        container: true,
        container_node: {
          target_id: "church entryway_1_2"
        },
        db_id: null,
        dead: false,
        desc: "A muddy area.",
        drink: false,
        equipped: null,
        food: false,
        food_energy: 0,
        gettable: false,
        locked_edge: null,
        name: "muddy area",
        name_prefix: "a",
        names: ["muddy area"],
        node_id: "muddy area_6_7",
        object: true,
        on_use: null,
        room: false,
        size: 1,
        stats: {
          damage: 0,
          defense: 0
        },
        surface_type: "in",
        value: 1,
        wearable: false,
        wieldable: false
      },
      orc_cave_0_1: {
        agent: false,
        classes: ["room"],
        contain_size: 100000,
        contained_nodes: {
          orc_2_4: {
            target_id: "orc_2_4"
          }
        },
        container_node: {
          target_id: "VOID"
        },
        db_id: null,
        desc: "It is a dark cave that is cold and damp inside. The floor is rocks covered in bat poop. It is damp from the ceiling dripping of water. The cave just goes on what seems to be endlessly into the dark abyss. The only light you can see is from the distance entrance of the cave.",
        extra_desc: "It is a dark cave that is cold and damp inside. The floor is rocks covered in bat poop. It is damp from the ceiling dripping of water. The cave just goes on what seems to be endlessly into the dark abyss. The only light you can see is from the distance entrance of the cave.",
        name: "Orc cave",
        name_prefix: "the",
        names: ["Orc cave"],
        neighbors: {
          church_entryway_1_2: {
            examine_desc: "You see a path!",
            label: "path to the east",
            locked_edge: null,
            target_id: "church entryway_1_2"
          }
        },
        node_id: "orc cave_0_1",
        object: false,
        room: true,
        size: 1,
        grid_location: [1, 0, 0],
        surface_type: "in"
      },
      orc_2_4: {
        agent: true,
        usually_npc: true,
        aggression: 0,
        char_type: "creature",
        classes: ["agent"],
        contain_size: 20,
        contained_nodes: {
          priceless_piece_of_art_4_3: {
            target_id: "priceless piece of art_4_3"
          }
        },
        container_node: {
          target_id: "orc cave_0_1"
        },
        damage: 1,
        db_id: null,
        defense: 0,
        desc: "You really don't have a good reason to be examining this orc closer.",
        followed_by: {},
        following: null,
        food_energy: 1,
        health: 10,
        is_player: false,
        name: "orc",
        name_prefix: "an",
        names: ["orc"],
        node_id: "orc_2_4",
        object: false,
        tags: ["orc"],
        attack_tagged_agents: ["!orc"],
        dont_accept_gifts: false,
        on_events: [
          [
            ["SayEvent", "lotr"],
            ["SayEvent", "One does not simply mention lotr!"]
          ],
          [
            ["SayEvent", "art"],
            [
              "SayEvent",
              "I might give you this piece of art if you give me something shiny for it."
            ]
          ],
          [
            ["SayEvent", "smile at me"],
            ["EmoteEvent", "smile"]
          ],
          [
            ["GiveObjectEvent", "ring"],
            ["GiveObjectEvent", "art", "other_agent"]
          ]
        ],
        persona: "I am a orc that was born in a cave. I eat corn the most. I have many friends.",
        room: false,
        size: 20,
        speed: 20
      },
      priceless_piece_of_art_4_3: {
        agent: false,
        classes: ["object"],
        contain_size: 0,
        contained_nodes: {},
        container: false,
        container_node: {
          target_id: "orc_2_4"
        },
        db_id: null,
        dead: false,
        desc: "A work of art that is has more than monetary value. Mostly owned by kings and wealthy collectors",
        drink: false,
        equipped: null,
        food: false,
        food_energy: 0,
        gettable: true,
        locked_edge: null,
        name: "priceless piece of art",
        name_prefix: "a",
        names: ["priceless piece of art"],
        node_id: "priceless piece of art_4_3",
        object: true,
        on_use: null,
        room: false,
        size: 1,
        stats: {
          damage: 0,
          defense: 0
        },
        surface_type: "on",
        value: 10,
        wearable: false,
        wieldable: true
      },
      shovel_5_6: {
        agent: false,
        classes: ["object"],
        contain_size: 0,
        contained_nodes: {},
        container: false,
        container_node: {
          target_id: "church entryway_1_2"
        },
        db_id: null,
        dead: false,
        desc: "A shovel",
        drink: false,
        equipped: null,
        food: false,
        food_energy: 0,
        gettable: true,
        locked_edge: null,
        name: "shovel",
        name_prefix: "a",
        names: ["shovel"],
        node_id: "shovel_5_6",
        object: true,
        on_use: [
            {
            remaining_uses: 1,
            events: [
              {
                type: "create_entity",
                params: {
                  type: "in_used_target_item",
                  object: {
                    name_prefix: "an",
                    is_wearable: true,
                    name: "emerald ring",
                    desc: "A beautiful and mysterious ring.. could it have magical powers?"
                  }
                }
              },
              {
                type: "broadcast_message",
                params: {
                  self_view: "You dig into the sodden mud, and spy something glistening within!"
                }
              }
            ],
            constraints: [
              {
                type: "is_holding",
                params: {
                  complement: "used_item"
                }
              },
              {
                type: "used_with_item_name",
                params: {
                  item: "muddy area"
                }
              }
            ]
          }
        ],
        room: false,
        size: 1,
        stats: {
          damage: 1,
          defense: 0
        },
        surface_type: "on",
        value: 1,
        wearable: false,
        wieldable: true
      },
      scroll_9_1: {
        agent: false,
        desc: "An old scroll with words you decipher to be: \"facere mortem\". Could this be magic?",
        name: "mortem scroll",
        drink: false,
        equipped: null,
        food: true,
        food_energy: 2,
        name_prefix: "a",
        value: 10,	
        node_id: "scroll_9_1",
        container_node: { 
            target_id: "church entryway_1_2" 
        },
        contained_nodes: {},
      object: true,
        on_use: [
          {
            events: [
              {
                type: "broadcast_message",
                params: {
                  self_view: "You say the words aloud, and runes on the scroll glow with gold.",
                  self_as_target_view: "You are struck with searing pain!",
                  self_not_target_view: "{recipient_text} is struck with searing pain!",
                  room_view: "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} is struck with searing pain!"
                }
              },
              {
                type: "modify_attribute",
                params: {
                  type: "in_used_target_item",
                  key: "health",
                  value: "-20"
                }
              }
            ],
            constraints: [
              {
                type: "is_holding",
                params: {
                  complement: "used_item"
                }
              },
              {
                type: "used_with_agent"
              }
            ]
          }
        ]
      },
      scroll_9_2: {
        agent: false,
        classes: ["object"],
        desc: "An old scroll with words you decipher to be: \"creo magnitudo\". Could this be magic?",
        name: "magnitudo scroll",
        name_prefix: "a",
        node_id: "scroll_9_2",
        container_node: { "target_id": "church entryway_1_2" },
        contained_nodes: {},
        object: true,
        on_use: [
          {
            events: [
              {
                type: "broadcast_message",
                params: {
                  self_view: "You say the words aloud, and runes on the scroll glow with gold.",
                  self_as_target_view: "Suddenly you feel a voluminous about you and you feel ... LARGER! You are  growing!",
                  self_not_target_view: "{recipient_text} appears to be growing larger!!!",
                  room_view: "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} seems to glow for a second.. and appears to be getting larger!"
                }
              },
              {
                type: "modify_attribute",
                params: {
                  type: "in_used_target_item",
                  key: "size",
                  value: "+2"
                }
              }
            ],
            constraints: [
              {
                type: "is_holding",
                params: {
                  complement: "used_item"
                }
              },
              {
                type: "used_with_agent"
              }
            ]
          }
        ]
      },
      scroll_9_3: {
        agent: false,
        classes: ["object"],
        desc: "An old scroll with words you decipher to be: \"creo dexteritate\". Could this be magic?",
        name: "dexteritate scroll",
        name_prefix: "a",
        node_id: "scroll_9_3",
        container_node: { "target_id": "church entryway_1_2" },
        contained_nodes: {},
        object: true,
        on_use: [
          {
            events: [
              {
                type: "broadcast_message",
                params: {
                  self_view: "You say the words aloud, and runes on the scroll glow with gold.",
                  self_as_target_view: "Suddenly you feel a lightness upon you and you feel more fleet of foot. Your dexterity has increased!",
                  self_not_target_view: "{recipient_text} feels a lightness upon them and they feel more fleet of foot. Their dexterity has increased!",
                  room_view: "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} seems to glow for a second."
                }
              },
              {
                type: "modify_attribute",
                params: {
                  type: "in_used_target_item",
                  key: "dexterity",
                  value: "+2"
                }
              }
            ],
            constraints: [
              {
                type: "is_holding",
                params: {
                  complement: "used_item"
                }
              },
              {
                type: "used_with_agent"
              }
            ]
          }
        ]
      }
    },
    objects: [
      "muddy area_6_7",
      "priceless piece of art_4_3",
      "shovel_5_6",
      "scroll_9_1",
      "scroll_9_2",
      "scroll_9_3"
    ],
    rooms: ["church entryway_1_2", "orc cave_0_1"]
}







//LARGE GAME SIZED WORLD WITH MANY NODES OF ALL SIZES

const ComplexWorld1 = {
  id:3,
  name: "Complex World",
  tags:["#red", "#haunted", "#dry"],
  agents: [
    "assassin_139",
    "assistant_chef_130",
    "bandit_153",
    "battle_master_99",
    "big_sheep_like_brown_dog_169",
    "bighorn_sheep_136",
    "butler_68",
    "drunk_reeling_out_of_the_163",
    "fox_150",
    "goblin_16",
    "graveyard_keeper_58",
    "groundskeeper_95",
    "half_wild_cat_123",
    "jailer_157",
    "lady_of_the_house_76",
    "lord_108",
    "master_at_arms_43",
    "milk_man_145",
    "monkey_friend_98",
    "pig_140",
    "priest_116",
    "rat_165",
    "serving_boy_51",
    "skeleton_assistant_15",
    "small_aggressive_looking_83",
    "smith_160",
    "town_doctor_142"
  ],
  nodes: {
    abandoned_farm_21: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1980,
      contained_nodes: {
        bighorn_sheep_136: {
          target_id: "bighorn_sheep_136"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "There's a bit of dust.",
      extra_desc: [
        "Sometimes things are just what they seem. There's nothing interesting here."
      ],
      grid_location: [
        2,
        1,
        0
      ],
      name: "Abandoned farm",
      name_prefix: "the",
      names: [
        "Abandoned farm"
      ],
      neighbors: {
        countryside_23: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "countryside_23"
        },
        the_forest_22: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "the_forest_22"
        },
        unsettling_forest_area_20: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "unsettling_forest_area_20"
        },
        wealthy_area_of_town_19: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "wealthy_area_of_town_19"
        }
      },
      node_id: "abandoned_farm_21",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    apple_tree_13: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 20,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "picnic_area_14"
      },
      db_id: null,
      dead: false,
      desc: "There are some delicious looking apples up there -- but they are too high to reach!",
      drink: 1,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 0,
      locked_edge: null,
      name: "apple tree",
      name_prefix: "an",
      names: [
        "apple tree"
      ],
      node_id: "apple_tree_13",
      object: true,
      on_use: null,
      room: false,
      size: 20,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "in",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    apron_133: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "assistant_chef_130"
      },
      db_id: null,
      dead: false,
      desc: "The apron is small and a picture of a fire is painted on its front.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "apron",
      name_prefix: "an",
      names: [
        "apron"
      ],
      node_id: "apron_133",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    assassin_139: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 20,
      contained_nodes: {},
      container_node: {
        target_id: "modest_living_area_18"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "This assassin holds no value for any life other than his own and will stop at nothing to achieve his goals.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Seek adventure, money and honor.",
      movement_energy_cost: 0,
      name: "assassin",
      name_prefix: "an",
      names: [
        "assassin"
      ],
      node_id: "assassin_139",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "Killing for a living puts things in perspective. It makes me appreciate life more. I would gladly annihilate all living beings for an appropriate fee.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    assistant_chef_130: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 15,
      contained_nodes: {
        apron_133: {
          target_id: "apron_133"
        },
        cookpot_131: {
          target_id: "cookpot_131"
        }
      },
      container_node: {
        target_id: "disposal_area_16"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "He is the bumbling but charming assistant to the chef, who has aspirations to become the head chef one day.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "I want to be the best chef in the world, and one day discover the perfect dish.",
      movement_energy_cost: 0,
      name: "assistant chef",
      name_prefix: "an",
      names: [
        "assistant chef"
      ],
      node_id: "assistant_chef_130",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I cook for the King and Queen and other Royals in the area. I take the directions from the head chef. I hope to someday be the head chef.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    bandit_153: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 18,
      contained_nodes: {
        harness_154: {
          target_id: "harness_154"
        },
        treasure_chest_155: {
          target_id: "treasure_chest_155"
        }
      },
      container_node: {
        target_id: "unsettling_forest_area_20"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "This bandit likes to steal items and hurt people.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "I want to pull of the greatest roberry there ever was. I may need to recruit some fellow bandits.",
      movement_energy_cost: 0,
      name: "bandit",
      name_prefix: "a",
      names: [
        "bandit"
      ],
      node_id: "bandit_153",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I steal items and money from others. I lurk on the side of the road and prey on travelers. I harm people.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    bathroom_pot_61: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      dead: false,
      desc: "The notorious pot holds a stale liquid.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "bathroom pot",
      name_prefix: "a",
      names: [
        "bathroom pot"
      ],
      node_id: "bathroom_pot_61",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    battle_master_99: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 14,
      contained_nodes: {
        cargo_100: {
          target_id: "cargo_100"
        },
        map_of_the_kingdom_102: {
          target_id: "map_of_the_kingdom_102"
        },
        paper_101: {
          target_id: "paper_101"
        }
      },
      container_node: {
        target_id: "small_hut_11"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "Most generals would oversee his during a battle but this one fights along side his men. You by his scratched and dinged up heavy plate mail armor. You can also tell by the men admire him while he is riding his gigantic battle steed across the battlefield with thundering hoof beats. You can tell by the fire in his eyes he does not do it for personal just to protect as many men under his leadership as he can.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Assess the threats to this nation, and possibly recruit more patriots.",
      movement_energy_cost: 0,
      name: "battle master",
      name_prefix: "a",
      names: [
        "battle master"
      ],
      node_id: "battle_master_99",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am the general's battle master. I oversee the troops during battles. I am the general's right hand man.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    bedding_65: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 1,
      contained_nodes: {
        luxurious_bedding_66: {
          target_id: "luxurious_bedding_66"
        },
        tent_67: {
          target_id: "tent_67"
        }
      },
      container: true,
      container_node: {
        target_id: "personal_quarters_2"
      },
      db_id: null,
      dead: false,
      desc: "The bedding is soft and warm, and is made out of silk and stuffed with animal feathers.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "bedding",
      name_prefix: "some",
      names: [
        "bedding"
      ],
      node_id: "bedding_65",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    bell_53: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "serving_boy_51"
      },
      db_id: null,
      dead: false,
      desc: "The bell is small and old, with a thin layer of tarnish that covers the silver. there's a small crack running down from the top.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "bell",
      name_prefix: "a",
      names: [
        "bell"
      ],
      node_id: "bell_53",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    big_sheep_like_brown_dog_169: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "creature",
      classes: [
        "agent"
      ],
      contain_size: 20,
      contained_nodes: {},
      container_node: {
        target_id: "outside_castle_32"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "A lovely and easy going creature that doesn't bother nobody.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Make friends with everyone! And who knows, they might feed, pet or play with me!",
      movement_energy_cost: 0,
      name: "big sheep-like brown dog",
      name_prefix: "a",
      names: [
        "big sheep-like brown dog"
      ],
      node_id: "big_sheep_like_brown_dog_169",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am a big sheep-like brown dog.  My owner is a poor farmer.  He feeds me scraps in the afternoon.  I sleep outside in the barn.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    bighorn_sheep_136: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 25,
      contained_nodes: {
        corn_137: {
          target_id: "corn_137"
        }
      },
      container_node: {
        target_id: "abandoned_farm_21"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The alpha ram dominates over all the other sheep in the flock. They step aside to allow him to be first at the food and water. Even humans coming running at the slightest bleating from his lips.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Find the best grazeable nibbles in the kingdom",
      movement_energy_cost: 0,
      name: "bighorn sheep",
      name_prefix: "a",
      names: [
        "bighorn sheep"
      ],
      node_id: "bighorn_sheep_136",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am a sheep with the biggest horns in the area. Other sheep give me food and drink. I know how to get humans to check on me.\nYour Mission: Find the best grazeable nibbles in the kingdom",
      quests: [
        {
          actor: "bighorn_sheep_136",
          actor_name: "bighorn sheep",
          actor_persona: "I am a sheep with the biggest horns in the area. Other sheep give me food and drink. I know how to get humans to check on me.\nYour Mission: Find the best grazeable nibbles in the kingdom",
          actor_str: "a bighorn sheep",
          agent: "half_wild_cat_123",
          container: null,
          goal_action: "give some corn to a half wild cat",
          goal_verb: "give",
          helper_agents: [],
          location: null,
          object: "corn_137",
          text: "I really need to give some corn to a half wild cat."
        }
      ],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    blacksmiths_hammer_128: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "half_wild_cat_123"
      },
      db_id: null,
      dead: false,
      desc: "The hammer is made of sturdy iron, but is covered in a layer of rust.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "blacksmith's hammer",
      name_prefix: "a",
      names: [
        "blacksmith's hammer"
      ],
      node_id: "blacksmiths_hammer_128",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    blanket_42: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "personal_rooms_0"
      },
      db_id: null,
      dead: false,
      desc: "The blanket is made from thick cotton, and it is a dull red color.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "blanket",
      name_prefix: "a",
      names: [
        "blanket"
      ],
      node_id: "blanket_42",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    block_and_tackle_111: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "lord_108"
      },
      db_id: null,
      dead: false,
      desc: "The block and tackle could be used to raise something.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "block and tackle",
      name_prefix: "a",
      names: [
        "block and tackle"
      ],
      node_id: "block_and_tackle_111",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    bottle_of_wine_164: {
      agent: false,
      classes: [
        "drink",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "drunk_reeling_out_of_the_163"
      },
      db_id: null,
      dead: false,
      desc: "The wine in the bottle appears rich and dark, inviting you to drink it.",
      drink: true,
      equipped: null,
      food: false,
      food_energy: 2,
      gettable: true,
      locked_edge: null,
      name: "bottle of wine",
      name_prefix: "a",
      names: [
        "bottle of wine"
      ],
      node_id: "bottle_of_wine_164",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    bow_and_arrows_82: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_gate_8"
      },
      db_id: null,
      dead: false,
      desc: "A bow an arrow. made from fine materials. mostly used for hunting and protection.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "bow and arrows",
      name_prefix: "a",
      names: [
        "bow and arrows"
      ],
      node_id: "bow_and_arrows_82",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    bow_81: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_gate_8"
      },
      db_id: null,
      dead: false,
      desc: "The bow is old and used, made of wood and some type of string.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "bow",
      name_prefix: "a",
      names: [
        "bow"
      ],
      node_id: "bow_81",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    bowl_of_fruit_94: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "small_graveyard_10"
      },
      db_id: null,
      dead: false,
      desc: "The bowl has a blue glaze, and holds a large mount of grapes and other fruit.",
      drink: false,
      equipped: null,
      food: true,
      food_energy: 3,
      gettable: true,
      locked_edge: null,
      name: "bowl of fruit",
      name_prefix: "a",
      names: [
        "bowl of fruit"
      ],
      node_id: "bowl_of_fruit_94",
      object: true,
      on_use: null,
      room: false,
      size: 3,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    broken_glass_36: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "personal_rooms_0"
      },
      db_id: null,
      dead: false,
      desc: "The glass is shattered in a hundred pieces, it is sharp and dangerous.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "broken glass",
      name_prefix: "some",
      names: [
        "broken glass"
      ],
      node_id: "broken_glass_36",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    bucket_for_eliminating_wa87: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      dead: false,
      desc: "The bucket is filled with a noxious brown liquid.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "bucket for eliminating waste",
      name_prefix: "a",
      names: [
        "bucket for eliminating waste"
      ],
      node_id: "bucket_for_eliminating_wa87",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    butler_68: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 17,
      contained_nodes: {
        chicken_69: {
          target_id: "chicken_69"
        },
        fresh_red_paint_70: {
          target_id: "fresh_red_paint_70"
        },
        sapphire_71: {
          target_id: "sapphire_71"
        }
      },
      container_node: {
        target_id: "personal_quarters_2"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "He is a well kept, tall man with many years of life experience that takes great pride in his duties and has a very matter of fact attitude usually reserved for royalty.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Make sure the royals have all their wishes met.",
      movement_energy_cost: 0,
      name: "butler",
      name_prefix: "a",
      names: [
        "butler"
      ],
      node_id: "butler_68",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I work for the royal family. I serve them food and beverages. I live in the worker's quarters of the castle.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    candle_114: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "wood_is_gathered_to_make_113"
      },
      db_id: null,
      dead: false,
      desc: "The candle smells of enchanting vanilla and wax drips down it's side. It has been used a few times but not overused",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "candle",
      name_prefix: "a",
      names: [
        "candle"
      ],
      node_id: "candle_114",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    candy_93: {
      agent: false,
      classes: [
        "food",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "small_graveyard_10"
      },
      db_id: null,
      dead: false,
      desc: "The candy is hard and shiny on the outside and made from sweet sugar and honey.",
      drink: false,
      equipped: null,
      food: true,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "candy",
      name_prefix: "a",
      names: [
        "candy"
      ],
      node_id: "candy_93",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    cannon_96: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "groundskeeper_95"
      },
      db_id: null,
      dead: false,
      desc: "The cannon is rusty, but still loaded.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "cannon",
      name_prefix: "a",
      names: [
        "cannon"
      ],
      node_id: "cannon_96",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    cargo_100: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "battle_master_99"
      },
      db_id: null,
      dead: false,
      desc: "The cargo is stacked up neatly.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "cargo",
      name_prefix: "some",
      names: [
        "cargo"
      ],
      node_id: "cargo_100",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    castle_34: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "This castle is made from red brick. The walls are all painted purple and have gold trim. There is a big chandelier that lights up the main room of the castle.",
      extra_desc: "The inside of the castle is where all important visitors come when in town. The kings throne is located in the castle and never moved. The inside of the castle gets a new coat of paint every month.",
      grid_location: [
        5,
        6,
        0
      ],
      name: "Castle",
      name_prefix: "the",
      names: [
        "Castle"
      ],
      neighbors: {
        outside_castle_32: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "outside_castle_32"
        },
        the_forsaken_castle_35: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "the_forsaken_castle_35"
        }
      },
      node_id: "castle_34",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    central_garden_4: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {
        pond_0: {
          target_id: "pond_0"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "There's a bit of dirt.",
      extra_desc: [
        "Sometimes things are just what they seem. There's nothing interesting here."
      ],
      grid_location: [
        4,
        4,
        0
      ],
      name: "Central garden",
      name_prefix: "the",
      names: [
        "Central garden"
      ],
      neighbors: {
        main_house_3: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "main_house_3"
        }
      },
      node_id: "central_garden_4",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    chair_5: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 20,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "wizards_quarters_3"
      },
      db_id: null,
      dead: false,
      desc: "The chair is inviting, but it is not the time to sit for a rest.",
      drink: 0,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 0,
      locked_edge: null,
      name: "chair",
      name_prefix: "a",
      names: [
        "chair"
      ],
      node_id: "chair_5",
      object: true,
      on_use: null,
      room: false,
      size: 20,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    chamber_pot_60: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "graveyard_keeper_58"
      },
      db_id: null,
      dead: false,
      desc: "The chamber pot smells terrible, like it has only been hastily emptied and not cleaned.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "chamber pot",
      name_prefix: "a",
      names: [
        "chamber pot"
      ],
      node_id: "chamber_pot_60",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    chamberpot_152: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "fox_150"
      },
      db_id: null,
      dead: false,
      desc: "The chamberpot is extremely clean, as though it never gets used.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "chamberpot",
      name_prefix: "a",
      names: [
        "chamberpot"
      ],
      node_id: "chamberpot_152",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    chicken_69: {
      agent: false,
      classes: [
        "food",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "butler_68"
      },
      db_id: null,
      dead: false,
      desc: "The chicken had a golden brown hue and was decorated with the finest vegetables that only fit for the king.",
      drink: false,
      equipped: null,
      food: true,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "chicken",
      name_prefix: "a",
      names: [
        "chicken"
      ],
      node_id: "chicken_69",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    clothes_made_of_various_p138: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "modest_living_area_18"
      },
      db_id: null,
      dead: false,
      desc: "The living vines that once hung in the trees now mask the flesh of man.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "clothes made of various plant matter such as large leaves and vines",
      name_prefix: "some",
      names: [
        "clothes made of various plant matter such as large leaves and vines"
      ],
      node_id: "clothes_made_of_various_p138",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    computer_48: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 1,
      contained_nodes: {
        hair_brush_50: {
          target_id: "hair_brush_50"
        },
        mystical_necklace_with_a_49: {
          target_id: "mystical_necklace_with_a_49"
        }
      },
      container: true,
      container_node: {
        target_id: "master_at_arms_43"
      },
      db_id: null,
      dead: false,
      desc: "The computer, also known as an abacus, is a wooden square with faded paint delicately holding metal rods and sliding beads.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "computer",
      name_prefix: "a",
      names: [
        "computer"
      ],
      node_id: "computer_48",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    cookpot_131: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 2,
      contained_nodes: {
        roasting_meat_132: {
          target_id: "roasting_meat_132"
        }
      },
      container: true,
      container_node: {
        target_id: "assistant_chef_130"
      },
      db_id: null,
      dead: false,
      desc: "The cookpot is large, heavy, and round. peering inside, you have trouble seeing the bottom.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "cookpot",
      name_prefix: "a",
      names: [
        "cookpot"
      ],
      node_id: "cookpot_131",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "in",
      value: 1,
      wearable: false,
      wieldable: false
    },
    corn_137: {
      agent: false,
      classes: [
        "food",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "bighorn_sheep_136"
      },
      db_id: null,
      dead: false,
      desc: "The corn is tasty and delicious, it is big and vast.",
      drink: false,
      equipped: null,
      food: true,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "corn",
      name_prefix: "some",
      names: [
        "corn"
      ],
      node_id: "corn_137",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    countryside_23: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1979,
      contained_nodes: {
        ink_jar_156: {
          target_id: "ink_jar_156"
        },
        jailer_157: {
          target_id: "jailer_157"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "The countryside is quite nice, it's not filled with a lot of people but with travelers here and there. Some in small groups some on their own. They are hosting a campfire where everyone has some to sit and is telling stories about their adventures. Someone is showing local children how to wield some weapons. Another is offering lodge, and stable for travelers and their animals.",
      extra_desc: "The countryside outside the bazaar has always been well known for being a place for people to relax. As they travel back and forth they can stop by campfires and share stories. It was first started by their king. A lovely man who wanted everyone to try and get to know each other and help each other. When he died his villagers wanted to continue his acts of kindness by offering help to those who passed by.",
      grid_location: [
        3,
        1,
        0
      ],
      name: "Countryside",
      name_prefix: "the",
      names: [
        "Countryside"
      ],
      neighbors: {
        abandoned_farm_21: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "abandoned_farm_21"
        },
        saokras_blacksmith_shop_25: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "saokras_blacksmith_shop_25"
        },
        shop_in_bazaar_24: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "shop_in_bazaar_24"
        }
      },
      node_id: "countryside_23",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    cup_134: {
      agent: false,
      classes: [
        "container",
        "object",
        "wieldable"
      ],
      contain_size: 2,
      contained_nodes: {
        spoon_135: {
          target_id: "spoon_135"
        }
      },
      container: true,
      container_node: {
        target_id: "table_area_17"
      },
      db_id: null,
      dead: false,
      desc: "The cup is old and broken, with the handle chipped from being dropped",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "cup",
      name_prefix: "a",
      names: [
        "cup"
      ],
      node_id: "cup_134",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    cupboard_11: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 18,
      contained_nodes: {
        scroll_7: {
          target_id: "scroll_7"
        },
        wizards_tome_12: {
          target_id: "wizards_tome_12"
        }
      },
      container: true,
      container_node: {
        target_id: "wizards_quarters_3"
      },
      db_id: null,
      dead: false,
      desc: "The cupboard is filled with all manner of dishware, its handles long worn down from constantly being opened and closed.",
      drink: 0,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 0,
      locked_edge: null,
      name: "cupboard",
      name_prefix: "a",
      names: [
        "cupboard"
      ],
      node_id: "cupboard_11",
      object: true,
      on_use: null,
      room: false,
      size: 20,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "in",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    dexteritate_scroll_9: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "lavish_desk_piled_high_wi6"
      },
      db_id: null,
      dead: false,
      desc: "An old scroll with words you decipher to be: \"creo dexteritate\". Could this be magic?",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "dexteritate scroll",
      name_prefix: "a",
      names: [
        "dexteritate scroll"
      ],
      node_id: "dexteritate_scroll_9",
      object: true,
      on_use: [
        {
          remaining_uses: 5,
          events: [
            {
              type: "broadcast_message",
              params: {
                room_view: "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} seems to glow for a second.",
                self_as_target_view: "Suddenly you feel a lightness upon you and you feel more fleet of foot. Your dexterity has increased!",
                self_not_target_view: "{recipient_text} feels a lightness upon them and they feel more fleet of foot. Their dexterity has increased!",
                self_view: "You say the words aloud, and runes on the scroll glow with gold."
              }
            },
            {
              type: "modify_attribute",
              params: {
                type: "in_used_target_item",
                key: "dexterity",
                value: "+2"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_agent"
            }
          ]
        }
      ],
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    disposal_area_16: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1978,
      contained_nodes: {
        assistant_chef_130: {
          target_id: "assistant_chef_130"
        },
        homestead_equipment_129: {
          target_id: "homestead_equipment_129"
        },
        shovel_1: {
          target_id: "shovel_1"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "It is piled high with trash. The smell is absolutely nauseating and the rats are multiplying faster than the castle can be rid of.",
      extra_desc: "It smells here!",
      grid_location: [
        1,
        3,
        0
      ],
      name: "Disposal area",
      name_prefix: "the",
      names: [
        "Disposal area"
      ],
      neighbors: {
        reception_area_12: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "reception_area_12"
        },
        table_area_17: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "table_area_17"
        }
      },
      node_id: "disposal_area_16",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    dress_88: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "small_aggressive_looking_83"
      },
      db_id: null,
      dead: false,
      desc: "The dress has beautiful frills and small jewels embedded on it",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "dress",
      name_prefix: "a",
      names: [
        "dress"
      ],
      node_id: "dress_88",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    drunk_reeling_out_of_the_163: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 20,
      contained_nodes: {
        bottle_of_wine_164: {
          target_id: "bottle_of_wine_164"
        }
      },
      container_node: {
        target_id: "table_area_17"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The town drunk fell down after being thrown our of the saloon.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Make friends with everyone! And.. well, hic! .. maybe a drink and a nap or too in between!",
      movement_energy_cost: 0,
      name: "drunk reeling out of the saloon",
      name_prefix: "a",
      names: [
        "drunk reeling out of the saloon"
      ],
      node_id: "drunk_reeling_out_of_the_163",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am known as the town drunk. I frequent the local pubs on a daily basis and drink beer till my belly is full. I commonly start fights with other patrons and get thrown out of the saloon.\nYour Mission: Make friends with everyone! And.. well, hic! .. maybe a drink and a nap or too in between!",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    dungeon_within_a_castle_2: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 100000,
      contained_nodes: {
        skeleton_assistant_15: {
          target_id: "skeleton_assistant_15"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "The castles dungeon lay buried below the village on the outskirts of the castles garden. Only the guards have access to light, and light is given as a privilege. The interior is stone and smells of mildew and deadly black mold.",
      extra_desc: "The castles dungeon lay buried below the village on the outskirts of the castles garden. Only the guards have access to light, and light is given as a privilege. The interior is stone and smells of mildew and deadly black mold.",
      grid_location: [
        1,
        -2,
        0
      ],
      name: "Dungeon within a castle",
      name_prefix: "the",
      names: [
        "Dungeon within a castle"
      ],
      neighbors: {
        dungeon_1: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "dungeon_1"
        },
        wizards_quarters_3: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "wizards_quarters_3"
        }
      },
      node_id: "dungeon_within_a_castle_2",
      object: false,
      room: true,
      size: 1,
      surface_type: "in"
    },
    dungeon_1: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 100000,
      contained_nodes: {
        goblin_16: {
          target_id: "goblin_16"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "A dirty stone room with tables and torture instruments abound.  There's pieces of equipment in various corners of the room.",
      extra_desc: "A dirty stone room with tables and torture instruments abound.  There's pieces of equipment in various corners of the room.",
      grid_location: [
        2,
        -2,
        0
      ],
      name: "Dungeon",
      name_prefix: "the",
      names: [
        "Dungeon"
      ],
      neighbors: {
        dungeon_within_a_castle_2: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "dungeon_within_a_castle_2"
        },
        entrance_to_a_cave_0: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "entrance_to_a_cave_0"
        }
      },
      node_id: "dungeon_1",
      object: false,
      room: true,
      size: 1,
      surface_type: "in"
    },
    embalming_equipment_90: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_graveyard_9"
      },
      db_id: null,
      dead: false,
      desc: "The equipment is remarkably clean.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "embalming equipment",
      name_prefix: "some",
      names: [
        "embalming equipment"
      ],
      node_id: "embalming_equipment_90",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    empty_storage_room_27: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "There's a bit of water.",
      extra_desc: [
        "Sometimes things are just what they seem. There's nothing interesting here."
      ],
      grid_location: [
        4,
        0,
        0
      ],
      name: "Empty storage room",
      name_prefix: "the",
      names: [
        "Empty storage room"
      ],
      neighbors: {
        fish_market_28: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "fish_market_28"
        },
        saokras_blacksmith_shop_25: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "saokras_blacksmith_shop_25"
        }
      },
      node_id: "empty_storage_room_27",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    entrance_to_a_cave_0: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 100000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "The snow drifts rise high enough that the entrance is difficult to make out.  Odd sounds and echos emerge from farther within, although whether they're caused by a trick of the wind or from something lurking within is hard to tell.  There are a few marks just within the entryway of the cave that look like they could be tracks of some kind, although they seem alarmingly large.",
      extra_desc: "The snow drifts rise high enough that the entrance is difficult to make out.  Odd sounds and echos emerge from farther within, although whether they're caused by a trick of the wind or from something lurking within is hard to tell.  There are a few marks just within the entryway of the cave that look like they could be tracks of some kind, although they seem alarmingly large.",
      grid_location: [
        2,
        -1,
        0
      ],
      name: "Entrance to a Cave",
      name_prefix: "the",
      names: [
        "Entrance to a Cave"
      ],
      neighbors: {
        dungeon_1: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "dungeon_1"
        },
        the_forest_22: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "the_forest_22"
        }
      },
      node_id: "entrance_to_a_cave_0",
      object: false,
      room: true,
      size: 1,
      surface_type: "in"
    },
    entrance_to_the_pine_tree15: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1999,
      contained_nodes: {
        hefty_rock_14: {
          target_id: "hefty_rock_14"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "Very tall and towering pine trees that create a dark canopy of shade. Long skinny trees sway in the sky from the soft breeze. Pine needles scatter the ground like plush carpet.",
      extra_desc: "The Pine forest is home to many deer and other animals. It is a sanctuary for people escaping the loud city. It is serene and peaceful and many people have found solace here.",
      grid_location: [
        0,
        4,
        0
      ],
      name: "Entrance to the Pine trees",
      name_prefix: "the",
      names: [
        "Entrance to the Pine trees"
      ],
      neighbors: {
        pine_tree_graveyard_13: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "pine_tree_graveyard_13"
        },
        reception_area_12: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "reception_area_12"
        }
      },
      node_id: "entrance_to_the_pine_tree15",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    expensive_carpet_37: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 1,
      contained_nodes: {
        ritual_dagger_39: {
          target_id: "ritual_dagger_39"
        },
        worn_quilt_38: {
          target_id: "worn_quilt_38"
        }
      },
      container: true,
      container_node: {
        target_id: "personal_rooms_0"
      },
      db_id: null,
      dead: false,
      desc: "A carpet made of the finest silk and with intricate patterns woven in.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "expensive carpet",
      name_prefix: "an",
      names: [
        "expensive carpet"
      ],
      node_id: "expensive_carpet_37",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    feather_fountain_pen_112: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "pine_tree_graveyard_13"
      },
      db_id: null,
      dead: false,
      desc: "The feather fountain pen appears to  have never been used before as it is so clean and shiny.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "feather fountain pen",
      name_prefix: "a",
      names: [
        "feather fountain pen"
      ],
      node_id: "feather_fountain_pen_112",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    finest_silk_and_velvet_158: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "jailer_157"
      },
      db_id: null,
      dead: false,
      desc: "The silk and velvet in the material make it feel so smooth.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "finest silk and velvet",
      name_prefix: "some",
      names: [
        "finest silk and velvet"
      ],
      node_id: "finest_silk_and_velvet_158",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    fish_market_28: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1980,
      contained_nodes: {
        rat_165: {
          target_id: "rat_165"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "The port is filled with many different small shops that sell fishes caught throughout the day. It is incredibly loud and busy with many customers and fisherman walking around and haggling for a good price on the fishes. There are tons of boxes sitting on the floors everywhere filled with ice, fish, and the fishermen's belongings.",
      extra_desc: "The port is right near the ocean and is a place where fisherman come to sell the fishes they caught throughout the early morning. It is a place of business where they sell more than just fish.",
      grid_location: [
        5,
        0,
        0
      ],
      name: "Fish Market",
      name_prefix: "the",
      names: [
        "Fish Market"
      ],
      neighbors: {
        empty_storage_room_27: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "empty_storage_room_27"
        }
      },
      node_id: "fish_market_28",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    fish_wrap__or_butcher_pap85: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "small_aggressive_looking_83"
      },
      db_id: null,
      dead: false,
      desc: "The fish wrap seems dirty and used, hopefully no one uses it.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "fish wrap ( or butcher paper)",
      name_prefix: "some",
      names: [
        "fish wrap ( or butcher paper)"
      ],
      node_id: "fish_wrap__or_butcher_pap85",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    fishing_rod_1: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "small_hut_11"
      },
      db_id: null,
      dead: false,
      desc: "Appears to be workable. Might be handy if you can find somewhere to fish!",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "fishing rod",
      name_prefix: "a",
      names: [
        "fishing rod"
      ],
      node_id: "fishing_rod_1",
      object: true,
      on_use: [
        {
          remaining_uses: "inf",
          events: [
            {
              type: "create_entity",
              params: {
                type: "in_actor",
                object: {
                  desc: "Mmm you could just eat this thing raw.",
                  is_food: 1,
                  is_wearable: false,
                  name: "tasty looking fish",
                  name_prefix: "a"
                }
              }
            },
            {
              type: "broadcast_message",
              params: {
                self_view: "You fish for a while..and oh my golly, you caught something!!"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_item_name",
              params: {
                item: "pond"
              }
            }
          ]
        }
      ],
      room: false,
      size: 1,
      stats: {
        damage: 1,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    flower_pot_75: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      dead: false,
      desc: "the pot is made of clay.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "flower pot",
      name_prefix: "a",
      names: [
        "flower pot"
      ],
      node_id: "flower_pot_75",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    food_tray_119: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "picnic_area_14"
      },
      db_id: null,
      dead: false,
      desc: "A simple tray, to put one's food on.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "food tray",
      name_prefix: "a",
      names: [
        "food tray"
      ],
      node_id: "food_tray_119",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    fox_150: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "creature",
      classes: [
        "agent"
      ],
      contain_size: 15,
      contained_nodes: {
        chamberpot_152: {
          target_id: "chamberpot_152"
        },
        sword_of_the_guards_151: {
          target_id: "sword_of_the_guards_151"
        }
      },
      container_node: {
        target_id: "unsettling_forest_area_20"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "This fox lives in the forest and steals from wanderers.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Tend to my family's needs -- beg, borrow or steal!",
      movement_energy_cost: 0,
      name: "fox",
      name_prefix: "a",
      names: [
        "fox"
      ],
      node_id: "fox_150",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am the fox of the brook in the forest. I live near the castle in the shrubs. I steal from wanderers.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    fresh_dry_house_shoes_72: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_house_3"
      },
      db_id: null,
      dead: false,
      desc: "The house shoes are freshly dried before being worn again.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "fresh dry house shoes",
      name_prefix: "some",
      names: [
        "fresh dry house shoes"
      ],
      node_id: "fresh_dry_house_shoes_72",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    fresh_red_paint_70: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "butler_68"
      },
      db_id: null,
      dead: false,
      desc: "The paint is a bright red color and easy to apply on a surface.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "fresh red paint",
      name_prefix: "some",
      names: [
        "fresh red paint"
      ],
      node_id: "fresh_red_paint_70",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    giant_club_46: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "master_at_arms_43"
      },
      db_id: null,
      dead: false,
      desc: "On further inspection of the giant club you notice it was stained with blood from the battle at the castle earlier.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "giant club",
      name_prefix: "a",
      names: [
        "giant club"
      ],
      node_id: "giant_club_46",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1,
        damage: 3
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    goblin_16: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "creature",
      classes: [
        "agent"
      ],
      contain_size: 20,
      contained_nodes: {},
      container_node: {
        target_id: "dungeon_1"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "Creeping out nightly comes the goblin to steal our children, turning them into soup for his dinner. In all the forest he is unwanted and unloved except by those of his own kind.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 6,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Make the best soup possible.",
      movement_energy_cost: 0,
      name: "goblin",
      name_prefix: "a",
      names: [
        "goblin"
      ],
      node_id: "goblin_16",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am a goblin that lives in the forest. I only come out at night. Sometimes I steal children and put them in a soup. No one likes me and I don't like anyone except for other goblins.",
      quests: [],
      room: false,
      size: 20,
      speed: 10,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    grappling_hook_56: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_hallway_1"
      },
      db_id: null,
      dead: false,
      desc: "The hook is rusty and has a sharp pointy end.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "grappling hook",
      name_prefix: "a",
      names: [
        "grappling hook"
      ],
      node_id: "grappling_hook_56",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    graveyard_keeper_58: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 14,
      contained_nodes: {
        chamber_pot_60: {
          target_id: "chamber_pot_60"
        },
        lush_green_vegetation_63: {
          target_id: "lush_green_vegetation_63"
        },
        name_placard_59: {
          target_id: "name_placard_59"
        }
      },
      container_node: {
        target_id: "main_hallway_1"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The graveyard keeper lives across the yard from the graveyard. He is always keeping an eye on the graveyard to make sure everything is in order and also digs all the new graves as needed.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Take care of the dead, and eventually run a funeral home.",
      movement_energy_cost: 0,
      name: "Graveyard Keeper",
      name_prefix: "a",
      names: [
        "Graveyard Keeper"
      ],
      node_id: "graveyard_keeper_58",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am the graveyard keeper who lives across the yard from the graveyard. I make sure all of the graves are marked and everything is in order. I dig the graves for newly deceased people.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    gray_stone_78: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_street_6"
      },
      db_id: null,
      dead: false,
      desc: "The stone is covered in mold",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "gray stone",
      name_prefix: "a",
      names: [
        "gray stone"
      ],
      node_id: "gray_stone_78",
      object: true,
      on_use: [
        {
          remaining_uses: "40",
          events: [
            {
              type: "create_entity",
              params: {
                type: "in_room",
                object: {
                  desc: "Mmm.. perfectly ripe.",
                  is_food: 1,
                  is_wearable: false,
                  name: "delicious crisp apple",
                  name_prefix: "a"
                }
              }
            },
            {
              type: "broadcast_message",
              params: {
                self_view: "You toss the stone.. and land a hit! You knock an apple right off!"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_item_name",
              params: {
                item: "apple tree"
              }
            }
          ]
        },
        {
          remaining_uses: "inf",
          events: [
            {
              type: "broadcast_message",
              params: {
                self_view: "You toss the stone.. and land a hit!"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_item_name",
              params: {
                item: "apple tree"
              }
            }
          ]
        }
      ],
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    groundskeeper_95: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 19,
      contained_nodes: {
        cannon_96: {
          target_id: "cannon_96"
        }
      },
      container_node: {
        target_id: "small_graveyard_10"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The groundskeeper skulks in the shadows, watching the archers as they practice with a look of both longing and hatred for what he cannot have.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Learn how to use a bow from the best.",
      movement_energy_cost: 0,
      name: "groundskeeper",
      name_prefix: "a",
      names: [
        "groundskeeper"
      ],
      node_id: "groundskeeper_95",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I trim the grass every two days.  I wish I could shoot the bow as the archers do.  I have been groundskeeper for 13 years.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    hair_brush_50: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "computer_48"
      },
      db_id: null,
      dead: false,
      desc: "The queen's ivory hair brush has horse hair bristles. It's pearly white handle is hand-carved and accented with jewels.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "hair brush",
      name_prefix: "a",
      names: [
        "hair brush"
      ],
      node_id: "hair_brush_50",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    half_wild_cat_123: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 14,
      contained_nodes: {
        blacksmiths_hammer_128: {
          target_id: "blacksmiths_hammer_128"
        },
        magical_crystal_127: {
          target_id: "magical_crystal_127"
        },
        magical_lights_124: {
          target_id: "magical_lights_124"
        },
        wooden_spit_125: {
          target_id: "wooden_spit_125"
        }
      },
      container_node: {
        target_id: "pine_tree_graveyard_13"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "He's a scruffy cat, rough around the edges, chasing mice in castle keep. Underneath there yet shines through the aura of a cat who once had better lodgings, who knew how to live in home with a hearth, a family and plenty of milk. Now he's become cold hearted and hardened scratching out at innocent bystanders and snatching their wee babes which he devours whole.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Trick people into giving me food, or if they are small enough, their life!",
      movement_energy_cost: 0,
      name: "half wild cat",
      name_prefix: "a",
      names: [
        "half wild cat"
      ],
      node_id: "half_wild_cat_123",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I used to live with people, but I was abandoned young to learn how to fend for myself. I like to scratch people. I love to eat their babies!\nYour Mission: Trick people into giving me food, or if they are small enough, their life!",
      quests: [
        {
          actor: "half_wild_cat_123",
          actor_name: "half wild cat",
          actor_persona: "I used to live with people, but I was abandoned young to learn how to fend for myself. I like to scratch people. I love to eat their babies!\nYour Mission: Trick people into giving me food, or if they are small enough, their life!",
          actor_str: "a half wild cat",
          agent: "serving_boy_51",
          container: null,
          goal_action: "a serving boy smiles",
          goal_verb: "smile",
          helper_agents: [],
          location: null,
          object: null,
          text: "I'd like to make a serving boy smile."
        }
      ],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    hand_plow_109: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "lord_108"
      },
      db_id: null,
      dead: false,
      desc: "The hand plow is used for farming the fresh earth",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "hand plow",
      name_prefix: "a",
      names: [
        "hand plow"
      ],
      node_id: "hand_plow_109",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    harness_154: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "bandit_153"
      },
      db_id: null,
      dead: false,
      desc: "The harness looks almost too big for a regular horse.  what type of animal is this for?",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "harness",
      name_prefix: "a",
      names: [
        "harness"
      ],
      node_id: "harness_154",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    hatchet_91: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "small_graveyard_10"
      },
      db_id: null,
      dead: false,
      desc: "The hatchet is old and worn out.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "hatchet",
      name_prefix: "a",
      names: [
        "hatchet"
      ],
      node_id: "hatchet_91",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    heavy_blanket_103: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "reception_area_12"
      },
      db_id: null,
      dead: false,
      desc: "The heavy blanket is incredibly comfortable.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "heavy blanket",
      name_prefix: "a",
      names: [
        "heavy blanket"
      ],
      node_id: "heavy_blanket_103",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    hefty_rock_14: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "entrance_to_the_pine_tree15"
      },
      db_id: null,
      dead: false,
      desc: "Feels good in the hand. Great for throwing at stuff!",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "hefty rock",
      name_prefix: "a",
      names: [
        "hefty rock"
      ],
      node_id: "hefty_rock_14",
      object: true,
      on_use: [
        {
          remaining_uses: "40",
          events: [
            {
              type: "create_entity",
              params: {
                type: "in_room",
                object: {
                  desc: "Mmm.. perfectly ripe.",
                  is_food: 1,
                  is_wearable: false,
                  name: "delicious crisp apple",
                  name_prefix: "a"
                }
              }
            },
            {
              type: "broadcast_message",
              params: {
                self_view: "You toss the stone.. and land a hit! You knock an apple right off!"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_item_name",
              params: {
                item: "apple tree"
              }
            }
          ]
        },
        {
          remaining_uses: "inf",
          events: [
            {
              type: "broadcast_message",
              params: {
                self_view: "You toss the stone.. and land a hit!"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_item_name",
              params: {
                item: "apple tree"
              }
            }
          ]
        }
      ],
      room: false,
      size: 1,
      stats: {
        damage: 1,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    homestead_equipment_129: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "disposal_area_16"
      },
      db_id: null,
      dead: false,
      desc: "The homestead equipment is ready to be used.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "homestead equipment",
      name_prefix: "some",
      names: [
        "homestead equipment"
      ],
      node_id: "homestead_equipment_129",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    horse_tack_89: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_graveyard_9"
      },
      db_id: null,
      dead: false,
      desc: "The horse tack is made of hardened leather and molded iron. it is designed perfectly to fit a horse.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "horse tack",
      name_prefix: "a",
      names: [
        "horse tack"
      ],
      node_id: "horse_tack_89",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    huge_cast_iron_pot_62: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      dead: false,
      desc: "The pot is large and black.  A large meal can be cooked in the pot.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "huge cast iron pot",
      name_prefix: "a",
      names: [
        "huge cast iron pot"
      ],
      node_id: "huge_cast_iron_pot_62",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    ink_jar_156: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "countryside_23"
      },
      db_id: null,
      dead: false,
      desc: "The ink in the jar swirls darkly, the glass glimmering in the light.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "ink jar",
      name_prefix: "an",
      names: [
        "ink jar"
      ],
      node_id: "ink_jar_156",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    ink_well_64: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "personal_quarters_2"
      },
      db_id: null,
      dead: false,
      desc: "The ink well sat in the king's chambers for use in mail.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "ink well",
      name_prefix: "an",
      names: [
        "ink well"
      ],
      node_id: "ink_well_64",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    ink_143: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "town_doctor_142"
      },
      db_id: null,
      dead: false,
      desc: "The ink is a bright red, reminiscent of blood.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "ink",
      name_prefix: "some",
      names: [
        "ink"
      ],
      node_id: "ink_143",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    jailer_157: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 18,
      contained_nodes: {
        finest_silk_and_velvet_158: {
          target_id: "finest_silk_and_velvet_158"
        },
        moldy_bread_159: {
          target_id: "moldy_bread_159"
        }
      },
      container_node: {
        target_id: "countryside_23"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "a good warring keep their prisoners in line.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Make sure everyone is doing their duty, within the royal law. (Unless I'm not on duty!)",
      movement_energy_cost: 0,
      name: "jailer",
      name_prefix: "a",
      names: [
        "jailer"
      ],
      node_id: "jailer_157",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am the jailer of the village. I keep the prisoners in line. I make sure the king's subjects stay in line.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    key_115: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "wood_is_gathered_to_make_113"
      },
      db_id: null,
      dead: false,
      desc: "The key is a large black skeleton key, seemingly made of wrought iron.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "key",
      name_prefix: "a",
      names: [
        "key"
      ],
      node_id: "key_115",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    lady_of_the_house_76: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 20,
      contained_nodes: {},
      container_node: {
        target_id: "main_house_3"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "a nice looking woman, smiling and giving a warm welcome.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Make the world a happier place, one tea party at a time.",
      movement_energy_cost: 0,
      name: "lady of the house",
      name_prefix: "a",
      names: [
        "lady of the house"
      ],
      node_id: "lady_of_the_house_76",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I love to accept guests.  I see to it that my house is clean.  I strive to make my guests comfortable.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    lance_110: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "lord_108"
      },
      db_id: null,
      dead: false,
      desc: "The knight's lance has an edge that bears the palpable scars of battle.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "lance",
      name_prefix: "a",
      names: [
        "lance"
      ],
      node_id: "lance_110",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1,
        damage: 3
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    large_earthenware_jug_of_74: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "main_house_3"
      },
      db_id: null,
      dead: false,
      desc: "The jug is simple earthenware with a bit of blue glaze around the rim.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "large earthenware jug of water for cooking and drinking",
      name_prefix: "a",
      names: [
        "large earthenware jug of water for cooking and drinking"
      ],
      node_id: "large_earthenware_jug_of_74",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    large_pile_of_hay_73: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_house_3"
      },
      db_id: null,
      dead: false,
      desc: "The pile of hay is large and dusty.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "large pile of hay",
      name_prefix: "a",
      names: [
        "large pile of hay"
      ],
      node_id: "large_pile_of_hay_73",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    lavish_desk_piled_high_wi6: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 19,
      contained_nodes: {
        dexteritate_scroll_9: {
          target_id: "dexteritate_scroll_9"
        }
      },
      container: true,
      container_node: {
        target_id: "wizards_quarters_3"
      },
      db_id: null,
      dead: false,
      desc: "The lavish desk is piled high with books that looked like they have seen years of use.  The leather bindings are cracked and the pages are yellowed and torn.  Under the books the desk has a beautiful maple top that reflected the sunlight from the window.",
      drink: 0,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 0,
      locked_edge: null,
      name: "lavish desk piled high with books",
      name_prefix: "a",
      names: [
        "lavish desk piled high with books"
      ],
      node_id: "lavish_desk_piled_high_wi6",
      object: true,
      on_use: null,
      room: false,
      size: 20,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    lord_108: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 17,
      contained_nodes: {
        block_and_tackle_111: {
          target_id: "block_and_tackle_111"
        },
        hand_plow_109: {
          target_id: "hand_plow_109"
        },
        lance_110: {
          target_id: "lance_110"
        }
      },
      container_node: {
        target_id: "reception_area_12"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The lord raised the taxes on his tenants, just because he could.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Survey my lands, and bask in my glory. And find ways to be even more glorious!",
      movement_energy_cost: 0,
      name: "lord",
      name_prefix: "a",
      names: [
        "lord"
      ],
      node_id: "lord_108",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am one of the king's lord.  I rule over a large area of land.  I have dozens of tenants.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    lush_green_vegetation_63: {
      agent: false,
      classes: [
        "food",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "graveyard_keeper_58"
      },
      db_id: null,
      dead: false,
      desc: "The plant is lush and well kept and remains fruitful to this day.",
      drink: false,
      equipped: null,
      food: true,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "lush green vegetation",
      name_prefix: "a",
      names: [
        "lush green vegetation"
      ],
      node_id: "lush_green_vegetation_63",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    luxurious_bedding_66: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "bedding_65"
      },
      db_id: null,
      dead: false,
      desc: "The bedding is soft and comforting, finely woven from the best wool.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "luxurious bedding",
      name_prefix: "some",
      names: [
        "luxurious bedding"
      ],
      node_id: "luxurious_bedding_66",
      object: true,
      on_use: null,
      room: false,
      size: 5,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 5,
      wearable: false,
      wieldable: false
    },
    mace_162: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "smith_160"
      },
      db_id: null,
      dead: false,
      desc: "The mace is sturdy and strong. you would hate to be hit by the metal spikes that line its head.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "mace",
      name_prefix: "a",
      names: [
        "mace"
      ],
      node_id: "mace_162",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    magical_crystal_127: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "half_wild_cat_123"
      },
      db_id: null,
      dead: false,
      desc: "The magical crystal is round and glowing.  it emits a white light.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "magical crystal",
      name_prefix: "a",
      names: [
        "magical crystal"
      ],
      node_id: "magical_crystal_127",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 100,
      wearable: false,
      wieldable: false
    },
    magical_lights_124: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "half_wild_cat_123"
      },
      db_id: null,
      dead: false,
      desc: "The shimmering magical light glistens of shades of blue and green from afar",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "magical lights",
      name_prefix: "some",
      names: [
        "magical lights"
      ],
      node_id: "magical_lights_124",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    magnitudo_scroll_10: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "shelf_4"
      },
      db_id: null,
      dead: false,
      desc: "An old scroll with words you decipher to be: \"creo magnitudo\". Could this be magic?",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 1,
      gettable: true,
      locked_edge: null,
      name: "magnitudo scroll",
      name_prefix: "a",
      names: [
        "magnitudo scroll"
      ],
      node_id: "magnitudo_scroll_10",
      object: true,
      on_use: [
        {
          remaining_uses: 5,
          events: [
            {
              type: "broadcast_message",
              params: {
                room_view: "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} seems to glow for a second.. and appears to be getting larger!",
                self_as_target_view: "Suddenly you feel a voluminous about you and you feel ... LARGER! You are  growing!",
                self_not_target_view: "{recipient_text} appears to be growing larger!!!",
                self_view: "You say the words aloud, and runes on the scroll glow with gold."
              }
            },
            {
              type: "modify_attribute",
              params: {
                type: "in_used_target_item",
                key: "size",
                value: "+2"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_agent"
            }
          ]
        }
      ],
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    main_entrance_7: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1998,
      contained_nodes: {
        suit_of_armor_79: {
          target_id: "suit_of_armor_79"
        },
        sword_80: {
          target_id: "sword_80"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "There are religious statues standing outside this temple.  The outside of the temple is fairly plain itself and imposing looking.  The floor is made out of stone with a bridge leading to the entrance.",
      extra_desc: "This is where all those who worship come through.  They are greeted by the impressive statues standing outside the temple.",
      grid_location: [
        3,
        6,
        0
      ],
      name: "Main entrance",
      name_prefix: "the",
      names: [
        "Main entrance"
      ],
      neighbors: {
        main_street_6: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "main_street_6"
        }
      },
      node_id: "main_entrance_7",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    main_gate_8: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1978,
      contained_nodes: {
        bow_and_arrows_82: {
          target_id: "bow_and_arrows_82"
        },
        bow_81: {
          target_id: "bow_81"
        },
        small_aggressive_looking_83: {
          target_id: "small_aggressive_looking_83"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "the main gate is new and guarded, it is not run down lie many parts of the area. it is meant to intimidate attackers by making them think the area is all new and not worn down.",
      extra_desc: "the gate being new was the idea of leaders, many resources were poured into the area, to the dismay of many members of the area",
      grid_location: [
        4,
        5,
        0
      ],
      name: "Main Gate",
      name_prefix: "the",
      names: [
        "Main Gate"
      ],
      neighbors: {
        main_street_6: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "main_street_6"
        },
        outside_castle_32: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "outside_castle_32"
        }
      },
      node_id: "main_gate_8",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    main_graveyard_9: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1998,
      contained_nodes: {
        embalming_equipment_90: {
          target_id: "embalming_equipment_90"
        },
        horse_tack_89: {
          target_id: "horse_tack_89"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "This is an ominous place that a thick fog envelops.  There are rows of primitive gravestones and crosses along with some angelic statues for the more wealthy.  You can hear sobs in the distance as a funeral ceremony is underway.",
      extra_desc: "Families of lost loved ones come here to grieve and pay their respects before the dead are buried.  Sometimes, in the dead of night, thieves come to rob the dead of their jewels.",
      grid_location: [
        2,
        5,
        0
      ],
      name: "Main graveyard",
      name_prefix: "the",
      names: [
        "Main graveyard"
      ],
      neighbors: {
        main_street_6: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "main_street_6"
        },
        small_graveyard_10: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "small_graveyard_10"
        }
      },
      node_id: "main_graveyard_9",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    main_hallway_1: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1978,
      contained_nodes: {
        grappling_hook_56: {
          target_id: "grappling_hook_56"
        },
        graveyard_keeper_58: {
          target_id: "graveyard_keeper_58"
        },
        torn_fabric_57: {
          target_id: "torn_fabric_57"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "This area is decorated with suits of armor, elaborate carpet pieces, and tapestries.  There's large, detailed paintings adorning the walls of past rulers.",
      extra_desc: "This is an area where a visitor can get a glimpse of the history of those who rule here.  It's meant to stun and impress those who enter.",
      grid_location: [
        4,
        3,
        0
      ],
      name: "Main hallway",
      name_prefix: "the",
      names: [
        "Main hallway"
      ],
      neighbors: {
        personal_rooms_0: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "personal_rooms_0"
        }
      },
      node_id: "main_hallway_1",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    main_house_3: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1974,
      contained_nodes: {
        fresh_dry_house_shoes_72: {
          target_id: "fresh_dry_house_shoes_72"
        },
        lady_of_the_house_76: {
          target_id: "lady_of_the_house_76"
        },
        large_earthenware_jug_of_74: {
          target_id: "large_earthenware_jug_of_74"
        },
        large_pile_of_hay_73: {
          target_id: "large_pile_of_hay_73"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "A fairly plain wooden building, the fireplace in the center of the back wall provides warmth during the winter seasons. There are paintings on the wall showing the farmer's forefathers and the previous owners. The floor is adorned with animal pelt rugs, and wood crafted furniture for the farmers to sit in.",
      extra_desc: "The main house provides refuge for the farmers after a hard days work, and is where they sleep, eat, and socialize before heading out for another day in the fields.",
      grid_location: [
        3,
        4,
        0
      ],
      name: "Main house",
      name_prefix: "the",
      names: [
        "Main house"
      ],
      neighbors: {
        central_garden_4: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "central_garden_4"
        },
        main_street_6: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "main_street_6"
        },
        personal_rooms_0: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "personal_rooms_0"
        },
        stretch_of_road_5: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "stretch_of_road_5"
        }
      },
      node_id: "main_house_3",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    main_street_6: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1998,
      contained_nodes: {
        gray_stone_78: {
          target_id: "gray_stone_78"
        },
        ritual_knife_77: {
          target_id: "ritual_knife_77"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "main street is bleak and outdated. it wears the atmosphere of the cemetery based on association. it is dark even in sunlight and has a unique odor",
      extra_desc: "many members of the town protested the cemetery being so close to the main street, but they were denied, and the atmosphere reflects this",
      grid_location: [
        3,
        5,
        0
      ],
      name: "Main street",
      name_prefix: "the",
      names: [
        "Main street"
      ],
      neighbors: {
        main_entrance_7: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "main_entrance_7"
        },
        main_gate_8: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "main_gate_8"
        },
        main_graveyard_9: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "main_graveyard_9"
        },
        main_house_3: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "main_house_3"
        }
      },
      node_id: "main_street_6",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    map_of_the_kingdom_102: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "battle_master_99"
      },
      db_id: null,
      dead: false,
      desc: "The map is very old and wrinkled, with one corner slightly torn.  the paper is yellowed.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "map of the kingdom",
      name_prefix: "a",
      names: [
        "map of the kingdom"
      ],
      node_id: "map_of_the_kingdom_102",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    master_at_arms_43: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 12,
      contained_nodes: {
        computer_48: {
          target_id: "computer_48"
        },
        giant_club_46: {
          target_id: "giant_club_46"
        },
        old_sun_bleached_sailclot44: {
          target_id: "old_sun_bleached_sailclot44"
        },
        shield_47: {
          target_id: "shield_47"
        },
        torch_45: {
          target_id: "torch_45"
        }
      },
      container_node: {
        target_id: "personal_rooms_0"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "He wears black.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Master every single weapon, hording a huge collection.",
      movement_energy_cost: 0,
      name: "master-at-arms",
      name_prefix: "a",
      names: [
        "master-at-arms"
      ],
      node_id: "master_at_arms_43",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am the master-at-arms. I work in the king's armory. I like to monitor all the weapons and make sure they are clean and sharp.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    materials_144: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "town_doctor_142"
      },
      db_id: null,
      dead: false,
      desc: "The material is lightweight and can be worn in the summer.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "materials",
      name_prefix: "some",
      names: [
        "materials"
      ],
      node_id: "materials_144",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    meat_161: {
      agent: false,
      classes: [
        "food",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "smith_160"
      },
      db_id: null,
      dead: false,
      desc: "As if fresh from the butcher shop, the meat is a vibrant blood red, and would surely make for a great meal once cooked.",
      drink: false,
      equipped: null,
      food: true,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "meat",
      name_prefix: "some",
      names: [
        "meat"
      ],
      node_id: "meat_161",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    metal_bucket_148: {
      agent: false,
      classes: [
        "container",
        "object",
        "wieldable"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "milk_man_145"
      },
      db_id: null,
      dead: false,
      desc: "The bucket is rusted and old.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 3,
      gettable: true,
      locked_edge: null,
      name: "metal bucket",
      name_prefix: "a",
      names: [
        "metal bucket"
      ],
      node_id: "metal_bucket_148",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    metal_meal_tray_120: {
      agent: false,
      classes: [
        "container",
        "object",
        "wieldable"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      dead: false,
      desc: "The tray is made of metal and is cool to the touch.  There are sections to put food on the tray.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "metal meal tray",
      name_prefix: "a",
      names: [
        "metal meal tray"
      ],
      node_id: "metal_meal_tray_120",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    milk_man_145: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 14,
      contained_nodes: {
        metal_bucket_148: {
          target_id: "metal_bucket_148"
        },
        milk_146: {
          target_id: "milk_146"
        },
        mug_of_mead_147: {
          target_id: "mug_of_mead_147"
        }
      },
      container_node: {
        target_id: "wealthy_area_of_town_19"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The milk man has lived just outside the town his entire life. His farm is tucked away in the rolling hills just north of the magnificent castle, where cattle roam about and feed on the grass here and there. He comes into town each day with fresh barrels of milk, furnishing everyone from peasants all the way up to lords. He enjoys his job, and has no enemies among the townspeople.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Own my own farm one day.",
      movement_energy_cost: 0,
      name: "milk man",
      name_prefix: "a",
      names: [
        "milk man"
      ],
      node_id: "milk_man_145",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am a milkman for the town in the kingdom. I bring fresh milk to town daily. I love working for the people of the town.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    milk_146: {
      agent: false,
      classes: [
        "drink",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "milk_man_145"
      },
      db_id: null,
      dead: false,
      desc: "The milk is curdled with flies floating in it.",
      drink: true,
      equipped: null,
      food: false,
      food_energy: 3,
      gettable: true,
      locked_edge: null,
      name: "milk",
      name_prefix: "a",
      names: [
        "milk"
      ],
      node_id: "milk_146",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    modest_living_area_18: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1959,
      contained_nodes: {
        assassin_139: {
          target_id: "assassin_139"
        },
        clothes_made_of_various_p138: {
          target_id: "clothes_made_of_various_p138"
        },
        pig_140: {
          target_id: "pig_140"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "Mud covered walls and a thatched roof cover the earthen, well-swept floor, packed hard from many generations of feet packing it hard. A fire burns brightly in the dim interior and a wood covered window is thrown wide to let the smoke escape. A few modest woven chairs and a fur skin rug are around the hearth, and a beaten copper pot hangs over the fire, simmering. The smell of mutton stew fills the room.",
      extra_desc: "The family who lives here has lived on the edge of the forest for generations, passed down from father to son, it has been the only home they have ever known in history. It is near the forest, but in a clearing so they have rich soils where they can grow vegetables, and hunt the forest for wild game. In the springtime, mother and her young ones will go out and pick berries and make delicious preserves.",
      grid_location: [
        0,
        2,
        0
      ],
      name: "Modest living area",
      name_prefix: "the",
      names: [
        "Modest living area"
      ],
      neighbors: {
        table_area_17: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "table_area_17"
        }
      },
      node_id: "modest_living_area_18",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    moldy_bread_159: {
      agent: false,
      classes: [
        "food",
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "jailer_157"
      },
      db_id: null,
      dead: false,
      desc: "The bread is moldy and is littered with green and black spots.",
      drink: false,
      equipped: true,
      food: true,
      food_energy: 2,
      gettable: true,
      locked_edge: null,
      name: "moldy bread",
      name_prefix: "some",
      names: [
        "moldy bread"
      ],
      node_id: "moldy_bread_159",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    monkey_friend_98: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "creature",
      classes: [
        "agent"
      ],
      contain_size: 20,
      contained_nodes: {},
      container_node: {
        target_id: "small_hut_11"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "an animal that is held in prominence.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Learn about the ways of humans. For my own ends, mwuhahaha. But they don't know that.",
      movement_energy_cost: 0,
      name: "monkey friend",
      name_prefix: "a",
      names: [
        "monkey friend"
      ],
      node_id: "monkey_friend_98",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am a monkey from the tropical forest. I am the only one who can speak with humans. I respect the king, but not the queen.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    mortem_scroll_8: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "shelf_4"
      },
      db_id: null,
      dead: false,
      desc: "An old scroll with words you decipher to be: \"facere mortem\". Could this be magic?",
      drink: false,
      equipped: null,
      food: true,
      food_energy: 2,
      gettable: true,
      locked_edge: null,
      name: "mortem scroll",
      name_prefix: "a",
      names: [
        "mortem scroll"
      ],
      node_id: "mortem_scroll_8",
      object: true,
      on_use: [
        {
          remaining_uses: 5,
          events: [
            {
              type: "broadcast_message",
              params: {
                room_view: "{actor_text} says the words of a scroll aloud, and it glows with gold. {recipient_text} is struck with searing pain!",
                self_as_target_view: "You are struck with searing pain!",
                self_not_target_view: "{recipient_text} is struck with searing pain!",
                self_view: "You say the words aloud, and runes on the scroll glow with gold."
              }
            },
            {
              type: "modify_attribute",
              params: {
                type: "in_used_target_item",
                key: "health",
                value: "-20"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_agent"
            }
          ]
        }
      ],
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    muddy_area_0: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 20,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "small_graveyard_10"
      },
      db_id: null,
      dead: false,
      desc: "This patch seems recently dug up.",
      drink: 1,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 0,
      locked_edge: null,
      name: "muddy area",
      name_prefix: "a",
      names: [
        "muddy area"
      ],
      node_id: "muddy_area_0",
      object: true,
      on_use: null,
      room: false,
      size: 20,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "in",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    mug_of_mead_147: {
      agent: false,
      classes: [
        "drink",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "milk_man_145"
      },
      db_id: null,
      dead: false,
      desc: "The mug of meed looks tempting.",
      drink: true,
      equipped: null,
      food: false,
      food_energy: 4,
      gettable: true,
      locked_edge: null,
      name: "mug of mead",
      name_prefix: "a",
      names: [
        "mug of mead"
      ],
      node_id: "mug_of_mead_147",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    mystical_necklace_with_a_49: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "computer_48"
      },
      db_id: null,
      dead: false,
      desc: "the mystical necklace is magical and scary",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "mystical necklace with a colorful crystal",
      name_prefix: "a",
      names: [
        "mystical necklace with a colorful crystal"
      ],
      node_id: "mystical_necklace_with_a_49",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 30,
      wearable: true,
      wieldable: false
    },
    name_placard_59: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "graveyard_keeper_58"
      },
      db_id: null,
      dead: false,
      desc: "The placard is made of wood with a clear name on it.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "name placard",
      name_prefix: "a",
      names: [
        "name placard"
      ],
      node_id: "name_placard_59",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    neptunes_throne_room_0: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 100000,
      contained_nodes: {
        throne_1: {
          target_id: "throne_1"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "A small room in the castle, Neptune's throne room is adorned with painted walls as blue as the sea itself. Tables constructed of beautiful coral lean against all four walls with decorative shells serving as a border for them. The ceiling is painted to resemble waves.",
      extra_desc: "A small room in the castle, Neptune's throne room is adorned with painted walls as blue as the sea itself. Tables constructed of beautiful coral lean against all four walls with decorative shells serving as a border for them. The ceiling is painted to resemble waves.",
      grid_location: [
        7,
        6,
        0
      ],
      name: "Neptune's throne room",
      name_prefix: "the",
      names: [
        "Neptune's throne room"
      ],
      neighbors: {
        the_forsaken_castle_35: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "the_forsaken_castle_35"
        }
      },
      node_id: "neptunes_throne_room_0",
      object: false,
      room: true,
      size: 1,
      surface_type: "in"
    },
    old_armor_170: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "the_forsaken_castle_35"
      },
      db_id: null,
      dead: false,
      desc: "The armor is rusted and dented.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "old armor",
      name_prefix: "an",
      names: [
        "old armor"
      ],
      node_id: "old_armor_170",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    old_broom_97: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "small_hut_11"
      },
      db_id: null,
      dead: false,
      desc: "The broom is very dusty and fragile.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "old broom",
      name_prefix: "an",
      names: [
        "old broom"
      ],
      node_id: "old_broom_97",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    old_prayer_books_54: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "serving_boy_51"
      },
      db_id: null,
      dead: false,
      desc: "The old prayer book is tattered and worn. it has markings all over it from a previous owner",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "old prayer books",
      name_prefix: "an",
      names: [
        "old prayer books"
      ],
      node_id: "old_prayer_books_54",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    old_sun_bleached_sailclot44: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "master_at_arms_43"
      },
      db_id: null,
      dead: false,
      desc: "The sailcloth has been bleached almost white by years of sunlight, and it is fraying at the edges.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "old, sun-bleached sailcloth",
      name_prefix: "an",
      names: [
        "old, sun-bleached sailcloth"
      ],
      node_id: "old_sun_bleached_sailclot44",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    orb_of_creation_2: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "throne_1"
      },
      db_id: null,
      dead: false,
      desc: "The orb glows bright blue and emits a powerful hum.",
      drink: 0,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 1,
      locked_edge: null,
      name: "orb of creation",
      name_prefix: "the",
      names: [
        "orb of creation"
      ],
      node_id: "orb_of_creation_2",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 1,
        defense: 0
      },
      surface_type: "in",
      value: 1,
      wearable: 0,
      wieldable: 1
    },
    ornate_goblet_41: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "personal_rooms_0"
      },
      db_id: null,
      dead: false,
      desc: "A goblet made of precious stones and gold.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "ornate goblet",
      name_prefix: "an",
      names: [
        "ornate goblet"
      ],
      node_id: "ornate_goblet_41",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    outside_castle_32: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1977,
      contained_nodes: {
        big_sheep_like_brown_dog_169: {
          target_id: "big_sheep_like_brown_dog_169"
        },
        rare_wood_from_a_tree_tha166: {
          target_id: "rare_wood_from_a_tree_tha166"
        },
        red_brick_167: {
          target_id: "red_brick_167"
        },
        salt_168: {
          target_id: "salt_168"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "The outside castle is beautifully decorated with priceless gems and artifacts. The stone used is ancient and antique with a shiny gloss of silver. The gardens outside the castle are a beautiful green and have the most delightful flowers.",
      extra_desc: "The outside castle was constructed in ancient times before any other building. It's concrete was one of the first ever used, and the stones used on the entrance door date back to the prehistoric age.",
      grid_location: [
        5,
        5,
        0
      ],
      name: "Outside Castle",
      name_prefix: "the",
      names: [
        "Outside Castle"
      ],
      neighbors: {
        castle_34: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "castle_34"
        },
        main_gate_8: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "main_gate_8"
        },
        unused_chamber_33: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "unused_chamber_33"
        }
      },
      node_id: "outside_castle_32",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    pail_105: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 2,
      contained_nodes: {
        water_pail_106: {
          target_id: "water_pail_106"
        }
      },
      container: true,
      container_node: {
        target_id: "reception_area_12"
      },
      db_id: null,
      dead: false,
      desc: "The pail is old and beginning to rust in places.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "pail",
      name_prefix: "a",
      names: [
        "pail"
      ],
      node_id: "pail_105",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    paper_101: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "battle_master_99"
      },
      db_id: null,
      dead: false,
      desc: "The paper is torn and yellowing around the edges.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "paper",
      name_prefix: "some",
      names: [
        "paper"
      ],
      node_id: "paper_101",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    personal_quarters_2: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1975,
      contained_nodes: {
        bedding_65: {
          target_id: "bedding_65"
        },
        butler_68: {
          target_id: "butler_68"
        },
        ink_well_64: {
          target_id: "ink_well_64"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "An ornate room, paintings of previous rulers and members of the family hang on the walls.  There's high end pieces of furniture in the room along with books, statues, and expensive pieces of jewelry.",
      extra_desc: "This is where the inhabitants of the palace come to rest, write, and do other personal activities.  Treasure is also stored here in hidden places only known to members of the royal family.",
      grid_location: [
        2,
        3,
        0
      ],
      name: "Personal quarters",
      name_prefix: "the",
      names: [
        "Personal quarters"
      ],
      neighbors: {
        personal_rooms_0: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "personal_rooms_0"
        }
      },
      node_id: "personal_quarters_2",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    personal_rooms_0: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1952,
      contained_nodes: {
        blanket_42: {
          target_id: "blanket_42"
        },
        broken_glass_36: {
          target_id: "broken_glass_36"
        },
        expensive_carpet_37: {
          target_id: "expensive_carpet_37"
        },
        master_at_arms_43: {
          target_id: "master_at_arms_43"
        },
        ornate_goblet_41: {
          target_id: "ornate_goblet_41"
        },
        serving_boy_51: {
          target_id: "serving_boy_51"
        },
        whip_40: {
          target_id: "whip_40"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "There is a comfortable, but not ornate bed against the wall in the center of the room. There is a dresser and a mirror against the opposite wall. There are various paintings hung throughout the room of landscapes and past kings and queens. There is a fireplace on the east wall with a bearskin rug on the floor in front of it, and two chairs to sit in.",
      extra_desc: "The personal room is used for guests to stay in while they visit the palace. The king and queen and the royal family stay in a different wing of the palace.",
      grid_location: [
        3,
        3,
        0
      ],
      name: "Personal rooms",
      name_prefix: "the",
      names: [
        "Personal rooms"
      ],
      neighbors: {
        main_hallway_1: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "main_hallway_1"
        },
        main_house_3: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "main_house_3"
        },
        personal_quarters_2: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "personal_quarters_2"
        }
      },
      node_id: "personal_rooms_0",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    picnic_area_14: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1994,
      contained_nodes: {
        apple_tree_13: {
          target_id: "apple_tree_13"
        },
        food_tray_119: {
          target_id: "food_tray_119"
        },
        rotting_meat_122: {
          target_id: "rotting_meat_122"
        },
        sleet_121: {
          target_id: "sleet_121"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "In this picnic area, there is a wide clearing with some cut down tree stumps made for people to sit and enjoy their lunch.  There's also a small pond nearby where people can feed fish and watch turtles sunbathe.",
      extra_desc: "Peasants come here during their lunch break to enjoy the outdoors before having to go back to their manual labor.  It's one of the few areas where they can unwind.",
      grid_location: [
        0,
        6,
        0
      ],
      name: "picnic area",
      name_prefix: "the",
      names: [
        "picnic area"
      ],
      neighbors: {
        pine_tree_graveyard_13: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "pine_tree_graveyard_13"
        }
      },
      node_id: "picnic_area_14",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    pig_140: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "creature",
      classes: [
        "agent"
      ],
      contain_size: 20,
      contained_nodes: {},
      container_node: {
        target_id: "modest_living_area_18"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The pig is lazy and gluttonous, and spends most of its days lounging in the mud and seeking out food.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Make everyone cheerful if I can. And wallow as much as possible! Not necessarily in that order.",
      movement_energy_cost: 0,
      name: "pig",
      name_prefix: "a",
      names: [
        "pig"
      ],
      node_id: "pig_140",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I love living in the mud. I eat just about anything. I am intelligent.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    pine_tree_graveyard_13: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1955,
      contained_nodes: {
        feather_fountain_pen_112: {
          target_id: "feather_fountain_pen_112"
        },
        half_wild_cat_123: {
          target_id: "half_wild_cat_123"
        },
        priest_116: {
          target_id: "priest_116"
        },
        wood_is_gathered_to_make_113: {
          target_id: "wood_is_gathered_to_make_113"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "Once known as a forest of solitude, the entrance to the pine trees is now a bleak and dreary graveyard.  Dead grass and moss fill the ground along with crawling critters that mark fear in the mind among the he who venture here.  Tombstones so old many of the names are no longer eligible.  Dense fog surrounds the area, thick tree tops blotting out the sunlight, and an eerie silence fills the air.  Cold it feels, the air, but the ground is soft and warm.  Sound can not enter, no escape this dwelling.",
      extra_desc: "The nearby town tells strangers that this place is peaceful and beautiful, but little do they know it is not.  A terrible price is paid for all visitors who enter this place, no one has ever returned.",
      grid_location: [
        0,
        5,
        0
      ],
      name: "Pine tree graveyard",
      name_prefix: "the",
      names: [
        "Pine tree graveyard"
      ],
      neighbors: {
        entrance_to_the_pine_tree15: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "entrance_to_the_pine_tree15"
        },
        picnic_area_14: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "picnic_area_14"
        },
        small_graveyard_10: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "small_graveyard_10"
        }
      },
      node_id: "pine_tree_graveyard_13",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    pond_0: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 20,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "central_garden_4"
      },
      db_id: null,
      dead: false,
      desc: "You think you see fish swimming in there!",
      drink: 1,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 0,
      locked_edge: null,
      name: "pond",
      name_prefix: "a",
      names: [
        "pond"
      ],
      node_id: "pond_0",
      object: true,
      on_use: null,
      room: false,
      size: 20,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "in",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    prayer_book_118: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "priest_116"
      },
      db_id: null,
      dead: false,
      desc: "The book contains many prayers. it has many pages and filled with many words on each.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "prayer book",
      name_prefix: "a",
      names: [
        "prayer book"
      ],
      node_id: "prayer_book_118",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    priceless_painting_52: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "serving_boy_51"
      },
      db_id: null,
      dead: false,
      desc: "The oil painting depicts the king's grandfather in an ermine robe. the painting is bright and lustrous.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "priceless painting",
      name_prefix: "a",
      names: [
        "priceless painting"
      ],
      node_id: "priceless_painting_52",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 300,
      wearable: false,
      wieldable: false
    },
    priest_116: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 18,
      contained_nodes: {
        prayer_book_118: {
          target_id: "prayer_book_118"
        },
        wooden_cross_117: {
          target_id: "wooden_cross_117"
        }
      },
      container_node: {
        target_id: "pine_tree_graveyard_13"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "This priest loves preaching and isn't afraid to be hard on people.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Help those in need.",
      movement_energy_cost: 0,
      name: "priest",
      name_prefix: "a",
      names: [
        "priest"
      ],
      node_id: "priest_116",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am here to help the needy. I am well respected in the town. I can not accept lying.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    primitive_fishing_pole_92: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "small_graveyard_10"
      },
      db_id: null,
      dead: false,
      desc: "The fishing pole was splintered and worn.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "primitive fishing pole",
      name_prefix: "a",
      names: [
        "primitive fishing pole"
      ],
      node_id: "primitive_fishing_pole_92",
      object: true,
      on_use: [
        {
          remaining_uses: "inf",
          events: [
            {
              type: "create_entity",
              params: {
                type: "in_actor",
                object: {
                  desc: "Mmm you could just eat this thing raw.",
                  is_food: 1,
                  is_wearable: false,
                  name: "tasty looking fish",
                  name_prefix: "a"
                }
              }
            },
            {
              type: "broadcast_message",
              params: {
                self_view: "You fish for a while..and oh my golly, you caught something!!"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_item_name",
              params: {
                item: "pond"
              }
            }
          ]
        }
      ],
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 5,
      wearable: false,
      wieldable: true
    },
    rare_wood_from_a_tree_tha166: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "outside_castle_32"
      },
      db_id: null,
      dead: false,
      desc: "The wood seems very unique in its attributes.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "rare wood from a tree that doesn't exist anymore",
      name_prefix: "a",
      names: [
        "rare wood from a tree that doesn't exist anymore"
      ],
      node_id: "rare_wood_from_a_tree_tha166",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 20,
      wearable: false,
      wieldable: false
    },
    rat_165: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "creature",
      classes: [
        "agent"
      ],
      contain_size: 20,
      contained_nodes: {},
      container_node: {
        target_id: "fish_market_28"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The rat never goes hungry because he lives near the shipping docks and steals food from cargo boxes that are loaded into ships every night.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Find the tastiest things, and the comfiest places to rest.",
      movement_energy_cost: 0,
      name: "rat",
      name_prefix: "a",
      names: [
        "rat"
      ],
      node_id: "rat_165",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I live near the docks on the edge of the city.  I steal food from cargo boxes that are loaded into ships at night.  Sometimes rats from strange lands come off ships that come to the dock.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    reception_area_12: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1974,
      contained_nodes: {
        heavy_blanket_103: {
          target_id: "heavy_blanket_103"
        },
        lord_108: {
          target_id: "lord_108"
        },
        pail_105: {
          target_id: "pail_105"
        },
        rock_104: {
          target_id: "rock_104"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "The building itself is ordinary in appearance and is somewhat foreboding.  It is surrounding by a dense fog and high grass.  Sometimes, one can hear whispers in the wind.",
      extra_desc: "This is a plain building where business matters of the graveyard are conducted.  Peasants and royalty alike come here to make deals to bury their loved ones in the graveyard.",
      grid_location: [
        1,
        4,
        0
      ],
      name: "Reception area",
      name_prefix: "the",
      names: [
        "Reception area"
      ],
      neighbors: {
        disposal_area_16: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "disposal_area_16"
        },
        entrance_to_the_pine_tree15: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "entrance_to_the_pine_tree15"
        },
        small_graveyard_10: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "small_graveyard_10"
        }
      },
      node_id: "reception_area_12",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    red_brick_167: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "outside_castle_32"
      },
      db_id: null,
      dead: false,
      desc: "The brick has crumbled and looked very weathered.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "red brick",
      name_prefix: "a",
      names: [
        "red brick"
      ],
      node_id: "red_brick_167",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    ritual_dagger_39: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "expensive_carpet_37"
      },
      db_id: null,
      dead: false,
      desc: "The ritual dagger has beautiful gems and engravings on the hilt.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "ritual dagger",
      name_prefix: "a",
      names: [
        "ritual dagger"
      ],
      node_id: "ritual_dagger_39",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    ritual_knife_77: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_street_6"
      },
      db_id: null,
      dead: false,
      desc: "A knife used in rituals by people. very decorative and intricate.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "ritual knife",
      name_prefix: "a",
      names: [
        "ritual knife"
      ],
      node_id: "ritual_knife_77",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    roasting_meat_132: {
      agent: false,
      classes: [
        "food",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "cookpot_131"
      },
      db_id: null,
      dead: false,
      desc: "The meat smells as though it were freshly cooked over a fire.",
      drink: false,
      equipped: null,
      food: true,
      food_energy: 4,
      gettable: true,
      locked_edge: null,
      name: "roasting meat",
      name_prefix: "some",
      names: [
        "roasting meat"
      ],
      node_id: "roasting_meat_132",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    rock_104: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "reception_area_12"
      },
      db_id: null,
      dead: false,
      desc: "The rock is smooth and heavy.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "rock",
      name_prefix: "a",
      names: [
        "rock"
      ],
      node_id: "rock_104",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    rotting_meat_122: {
      agent: false,
      classes: [
        "food",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "picnic_area_14"
      },
      db_id: null,
      dead: false,
      desc: "The meat is rotting and it smells badly almost to the point of nausea.",
      drink: false,
      equipped: null,
      food: true,
      food_energy: -2,
      gettable: true,
      locked_edge: null,
      name: "rotting meat",
      name_prefix: "some",
      names: [
        "rotting meat"
      ],
      node_id: "rotting_meat_122",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    salt_168: {
      agent: false,
      classes: [
        "food",
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "outside_castle_32"
      },
      db_id: null,
      dead: false,
      desc: "The salt is clean and white, looking more like a crystal than something to eat.",
      drink: false,
      equipped: null,
      food: true,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "salt",
      name_prefix: "some",
      names: [
        "salt"
      ],
      node_id: "salt_168",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    saokras_blacksmith_shop_25: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1980,
      contained_nodes: {
        smith_160: {
          target_id: "smith_160"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "Saokra's Blacksmith Shop is lined with weapons. They are shown through the outside windows, and once you step inside you see everything from bo staffs to canons. Most of the shop is cool for the work that goes on inside. There are dozens of painted maps on the walls and ceiling. There's a bookshelf over to the left side of the shop that holds nothing but rolled up scrolls, and some have fallen to the floor. Armor sets adorn the manikins to the back of the room. There's a vibrant royal blue knight set of armor that causes the back area to light up in a cool glow of blue. The middle of the room has sunlight beaming into it via a skylight that gives the area a warm feeling.",
      extra_desc: "Saokra's Shop has been around for years, Saokra herself has always been the owner of it. No one's sure how but it's believed that she was once a God, and possibly still is but instead of living her life in the heavens she chose to live with the people and enjoys her work. One of the reasons for this is that the shop in question seemed to be around for more than a hundred years and with each weapon or armor set she creates you can feel a hum within it. No one's sure why she decided to live the life she does but everyone is grateful to her for having helped keep some of the bad souls away.",
      grid_location: [
        4,
        1,
        0
      ],
      name: "Saokra's Blacksmith Shop",
      name_prefix: "the",
      names: [
        "Saokra's Blacksmith Shop"
      ],
      neighbors: {
        countryside_23: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "countryside_23"
        },
        empty_storage_room_27: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "empty_storage_room_27"
        },
        town_26: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "town_26"
        }
      },
      node_id: "saokras_blacksmith_shop_25",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    sapphire_71: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "butler_68"
      },
      db_id: null,
      dead: false,
      desc: "The sapphire is beautiful.  the gem emits a dark blue light.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "sapphire",
      name_prefix: "a",
      names: [
        "sapphire"
      ],
      node_id: "sapphire_71",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 100,
      wearable: false,
      wieldable: false
    },
    scrap_of_fur_141: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "wealthy_area_of_town_19"
      },
      db_id: null,
      dead: false,
      desc: "The scrap of fur is matted and tiny insects crawl upon it.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "scrap of fur",
      name_prefix: "a",
      names: [
        "scrap of fur"
      ],
      node_id: "scrap_of_fur_141",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    scroll_7: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "cupboard_11"
      },
      db_id: null,
      dead: false,
      desc: 'The scroll contains an oddly written text. You hardly recognize the language. There is a faded drawing of an emerald looking ring and the words "locus aliquid"',
      drink: 0,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 1,
      locked_edge: null,
      name: "scroll",
      name_prefix: "a",
      names: [
        "scroll"
      ],
      node_id: "scroll_7",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "in",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    serving_boy_51: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 16,
      contained_nodes: {
        bell_53: {
          target_id: "bell_53"
        },
        old_prayer_books_54: {
          target_id: "old_prayer_books_54"
        },
        priceless_painting_52: {
          target_id: "priceless_painting_52"
        },
        wall_hanging_55: {
          target_id: "wall_hanging_55"
        }
      },
      container_node: {
        target_id: "personal_rooms_0"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The young man darts past you, obviously with places to be. He sure seems so young to be moving with such purpose.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Better myself and become a high ranking official one day when I grow up.",
      movement_energy_cost: 0,
      name: "serving boy",
      name_prefix: "a",
      names: [
        "serving boy"
      ],
      node_id: "serving_boy_51",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am the son of the butler in the castle. I assist my father in serving the King and Queen. I live in the servant's quarters of the castle along with my mother and 2 sisters.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    shelf_4: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 18,
      contained_nodes: {
        magnitudo_scroll_10: {
          target_id: "magnitudo_scroll_10"
        },
        mortem_scroll_8: {
          target_id: "mortem_scroll_8"
        }
      },
      container: true,
      container_node: {
        target_id: "wizards_quarters_3"
      },
      db_id: null,
      dead: false,
      desc: "The shelf is sturdy and held in place with rusty iron brackets.  It held a collection of vials and potions.  The bottles are dusty and looked like they've been there for years.",
      drink: 0,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 0,
      locked_edge: null,
      name: "shelf",
      name_prefix: "a",
      names: [
        "shelf"
      ],
      node_id: "shelf_4",
      object: true,
      on_use: null,
      room: false,
      size: 20,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    shield_47: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "master_at_arms_43"
      },
      db_id: null,
      dead: false,
      desc: "The circular wooden shield has a leather rim and a striking metallic boss in the shape of a dragon's head, at the center.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "shield",
      name_prefix: "a",
      names: [
        "shield"
      ],
      node_id: "shield_47",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1,
        defense: 2
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    shop_in_bazaar_24: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "This looks like a lean-to tent.  Propped up on three sides by branches and there is a table in the middle.  The proprietor is selling certain jewels that he claims will provide protection.  They are all different colors and he is well versed in what kind of protection they will provide.",
      extra_desc: "This tent in the bazaar has been a long time coming.  The proprietor has gone all over the kingdom looking for these stones to make a living.  He really doesn't believe in their powers, but a lady who claimed to be a sorceress that he met in the countryside promised him that if he found these stones and sold them to the townspeople, that he would be greatly rewarded.  So he has spent the better part of the year collecting these jewels.",
      grid_location: [
        3,
        0,
        0
      ],
      name: "Shop in Bazaar",
      name_prefix: "the",
      names: [
        "Shop in Bazaar"
      ],
      neighbors: {
        countryside_23: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "countryside_23"
        },
        the_forest_22: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "the_forest_22"
        }
      },
      node_id: "shop_in_bazaar_24",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    shovel_1: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "disposal_area_16"
      },
      db_id: null,
      dead: false,
      desc: "A shovel",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "shovel",
      name_prefix: "a",
      names: [
        "shovel"
      ],
      node_id: "shovel_1",
      object: true,
      on_use: [
        {
          remaining_uses: 1,
          events: [
            {
              type: "create_entity",
              params: {
                type: "in_used_target_item",
                object: {
                  name_prefix: "an",
                  is_wearable: true,
                  name: "emerald ring",
                  desc: "A beautiful and mysterious ring.. could it have magical powers?"
                }
              }
            },
            {
              type: "broadcast_message",
              params: {
                self_view: "You dig into the sodden mud, and spy something glistening within!"
              }
            }
          ],
          constraints: [
            {
              type: "is_holding",
              params: {
                complement: "used_item"
              }
            },
            {
              type: "used_with_item_name",
              params: {
                item: "muddy area"
              }
            }
          ]
        }
      ],
      room: false,
      size: 1,
      stats: {
        damage: 1,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    skeleton_assistant_15: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "creature",
      classes: [
        "agent"
      ],
      contain_size: 21,
      contained_nodes: {},
      container_node: {
        target_id: "dungeon_within_a_castle_2"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "You are a much better assistant than the rest, taking up no space, no back talking, and you do what is told.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 6,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Aid my Wizard master in their goals.",
      movement_energy_cost: 0,
      name: "skeleton assistant",
      name_prefix: "a",
      names: [
        "skeleton assistant"
      ],
      node_id: "skeleton_assistant_15",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I was created by my master to assist him in his endeavors. I make many mistakes as I have no brain and therefore no critical thinking skills. I am also extremely clumsy as my depth perception is lacking with out actual eyeballs.",
      quests: [
        {
          actor: "skeleton_assistant_15",
          actor_name: "skeleton assistant",
          actor_persona: "I was created by my master to assist him in his endeavors. I make many mistakes as I have no brain and therefore no critical thinking skills. I am also extremely clumsy as my depth perception is lacking with out actual eyeballs.",
          actor_str: "a skeleton assistant",
          agent: "drunk_reeling_out_of_the_163",
          container: null,
          goal_action: "a drunk reeling out of the saloon smiles",
          goal_verb: "smile",
          helper_agents: [],
          location: null,
          object: null,
          text: "I'd like to make a drunk reeling out of the saloon smile."
        }
      ],
      reward_xp: 0,
      room: false,
      size: 20,
      speed: 10,
      strength: 0,
      tags: [],
      usually_npc: false,
      xp: 0
    },
    sleet_121: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "picnic_area_14"
      },
      db_id: null,
      dead: false,
      desc: "The sleet is so thick it is hard to see the floor.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "sleet",
      name_prefix: "some",
      names: [
        "sleet"
      ],
      node_id: "sleet_121",
      object: true,
      on_use: null,
      room: false,
      size: 100,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    small_aggressive_looking_83: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "creature",
      classes: [
        "agent"
      ],
      contain_size: 13,
      contained_nodes: {
        dress_88: {
          target_id: "dress_88"
        },
        fish_wrap__or_butcher_pap85: {
          target_id: "fish_wrap__or_butcher_pap85"
        },
        small_bucket_86: {
          target_id: "small_bucket_86"
        },
        small_crucifix_84: {
          target_id: "small_crucifix_84"
        }
      },
      container_node: {
        target_id: "main_gate_8"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "This dog may be small but that doesnt stop him from fighting the other hungry dogs for food.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Make friends with the right ones, make enemies of the wrong ones.",
      movement_energy_cost: 0,
      name: "small aggressive-looking dog",
      name_prefix: "a",
      names: [
        "small aggressive-looking dog"
      ],
      node_id: "small_aggressive_looking_83",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "No one likes dogs. I live on the streets with all the other dogs. I am hungry most of the time. Sometimes I fight with the other dogs. I am a dog.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    small_bucket_86: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "small_aggressive_looking_83"
      },
      db_id: null,
      dead: false,
      desc: "The bucket may be small but it gets the job done.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "small bucket",
      name_prefix: "a",
      names: [
        "small bucket"
      ],
      node_id: "small_bucket_86",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    small_crucifix_84: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "small_aggressive_looking_83"
      },
      db_id: null,
      dead: false,
      desc: "A small crucifix does not necessarily mean small faith.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "small crucifix",
      name_prefix: "a",
      names: [
        "small crucifix"
      ],
      node_id: "small_crucifix_84",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    small_graveyard_10: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1973,
      contained_nodes: {
        bowl_of_fruit_94: {
          target_id: "bowl_of_fruit_94"
        },
        candy_93: {
          target_id: "candy_93"
        },
        groundskeeper_95: {
          target_id: "groundskeeper_95"
        },
        hatchet_91: {
          target_id: "hatchet_91"
        },
        muddy_area_0: {
          target_id: "muddy_area_0"
        },
        primitive_fishing_pole_92: {
          target_id: "primitive_fishing_pole_92"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "This is a small grassy area located under a large oak tree.  There are two home made wooden crosses set up along with mounds where the bodies are buried.",
      extra_desc: "This is where the residents of the cottage have buried their loved ones.  They wanted them to be close by so they can pay their respects.",
      grid_location: [
        1,
        5,
        0
      ],
      name: "Small graveyard",
      name_prefix: "the",
      names: [
        "Small graveyard"
      ],
      neighbors: {
        main_graveyard_9: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "main_graveyard_9"
        },
        pine_tree_graveyard_13: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "pine_tree_graveyard_13"
        },
        reception_area_12: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "reception_area_12"
        },
        small_hut_11: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "small_hut_11"
        }
      },
      node_id: "small_graveyard_10",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    small_hut_11: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1958,
      contained_nodes: {
        battle_master_99: {
          target_id: "battle_master_99"
        },
        fishing_rod_1: {
          target_id: "fishing_rod_1"
        },
        monkey_friend_98: {
          target_id: "monkey_friend_98"
        },
        old_broom_97: {
          target_id: "old_broom_97"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "Very small, inside and out, the small hut is made of straw that has turned dingy from mold and time. Two cutout for windows and a brown cloth door mark the front entrance. Inside, there is only a wooden chair and table upon which sits a small wooden bowl and spoon.",
      extra_desc: "The hut belongs to Jacob, a man who got lost in the jungle and made himself a home to shield and protect him from the elements, animals, and bugs.",
      grid_location: [
        1,
        6,
        0
      ],
      name: "Small Hut",
      name_prefix: "the",
      names: [
        "Small Hut"
      ],
      neighbors: {
        small_graveyard_10: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "small_graveyard_10"
        }
      },
      node_id: "small_hut_11",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    small_metal_bucket_149: {
      agent: false,
      classes: [
        "container",
        "object",
        "wieldable"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      dead: false,
      desc: "The metal bucket appears to be made of copper, with multiple dents and scratches on the the surface.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "small metal bucket",
      name_prefix: "a",
      names: [
        "small metal bucket"
      ],
      node_id: "small_metal_bucket_149",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    smith_160: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 18,
      contained_nodes: {
        mace_162: {
          target_id: "mace_162"
        },
        meat_161: {
          target_id: "meat_161"
        }
      },
      container_node: {
        target_id: "saokras_blacksmith_shop_25"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "Sooty and sweaty labors the smith over his furnace. With brute and brawn he fashions the finest quality steel in the land into weapons of war.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Find the one who is worthy, and forge the greatest blade ever made.",
      movement_energy_cost: 0,
      name: "smith",
      name_prefix: "a",
      names: [
        "smith"
      ],
      node_id: "smith_160",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "My forge is over a thousand degrees. I can melt steel with ore and wood. I make only the finest quality blades and armor.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    spoon_135: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "cup_134"
      },
      db_id: null,
      dead: false,
      desc: "The spoon is rustic looking, as though it was carved hastily.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "spoon",
      name_prefix: "a",
      names: [
        "spoon"
      ],
      node_id: "spoon_135",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    stretch_of_road_5: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "There's a bit of water.",
      extra_desc: [
        "Sometimes things are just what they seem. There's nothing interesting here."
      ],
      grid_location: [
        2,
        4,
        0
      ],
      name: "Stretch of road",
      name_prefix: "the",
      names: [
        "Stretch of road"
      ],
      neighbors: {
        main_house_3: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "main_house_3"
        }
      },
      node_id: "stretch_of_road_5",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    suit_of_armor_79: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_entrance_7"
      },
      db_id: null,
      dead: false,
      desc: "The suit of armor was highly polished and it gleamed in the light.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "suit of armor",
      name_prefix: "a",
      names: [
        "suit of armor"
      ],
      node_id: "suit_of_armor_79",
      object: true,
      on_use: null,
      room: false,
      size: 5,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    sword_of_the_guards_151: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "fox_150"
      },
      db_id: null,
      dead: false,
      desc: "The sword is sturdy and so heavy that you have trouble lifting it.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "sword of the guards",
      name_prefix: "a",
      names: [
        "sword of the guards"
      ],
      node_id: "sword_of_the_guards_151",
      object: true,
      on_use: null,
      room: false,
      size: 3,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    sword_80: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_entrance_7"
      },
      db_id: null,
      dead: false,
      desc: "Sword's blade was sharp and sturdy. holding it, you could tell it is well versed in the art of war, and is no stranger to the taste of blood, bone and steel.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "sword",
      name_prefix: "a",
      names: [
        "sword"
      ],
      node_id: "sword_80",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    table_area_17: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1976,
      contained_nodes: {
        cup_134: {
          target_id: "cup_134"
        },
        drunk_reeling_out_of_the_163: {
          target_id: "drunk_reeling_out_of_the_163"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "A floor where musicians and other acts perform as well and dancing and other types of entertainment for the patrons of the tavern. Its a nice place suitable for people who want to enjoy an evening. Hearing music, stories and other entertainments.",
      extra_desc: "People from the town and the countryside go to have fun, catch up, and to see what has been happening around the town. While they're here they often find some interesting entertainment from whoever happens to be performing in the tavern today.",
      grid_location: [
        1,
        2,
        0
      ],
      name: "table area",
      name_prefix: "the",
      names: [
        "table area"
      ],
      neighbors: {
        disposal_area_16: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "disposal_area_16"
        },
        modest_living_area_18: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "modest_living_area_18"
        },
        unsettling_forest_area_20: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "unsettling_forest_area_20"
        },
        wealthy_area_of_town_19: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "wealthy_area_of_town_19"
        }
      },
      node_id: "table_area_17",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    tent_67: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "bedding_65"
      },
      db_id: null,
      dead: false,
      desc: "The tent looks empty.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "tent",
      name_prefix: "a",
      names: [
        "tent"
      ],
      node_id: "tent_67",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    the_forest_22: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "The forest has many trees. It has other plants too. There are animals and many livings things. The forest is very much full of life. When you look at it you might only see plants that are green and different shades of brown but there are many other living things in there too.",
      extra_desc: "The forest started out as a small amount of plants and then the plants kept growing and growing until they were vast. After the plants were very grown the animals and all the small livings things decided to make some houses in the plants.",
      grid_location: [
        2,
        0,
        0
      ],
      name: "forest",
      name_prefix: "the",
      names: [
        "The forest"
      ],
      neighbors: {
        abandoned_farm_21: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "abandoned_farm_21"
        },
        entrance_to_a_cave_0: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "entrance_to_a_cave_0"
        },
        shop_in_bazaar_24: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "shop_in_bazaar_24"
        }
      },
      node_id: "the_forest_22",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    the_forsaken_castle_35: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1999,
      contained_nodes: {
        old_armor_170: {
          target_id: "old_armor_170"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "Old and creepy, the castle has been abandoned for centuries now. It is broken and destroyed.",
      extra_desc: "The castle use to belong to a kingdom. It was a beautiful and rich kingdom, but the people were murdered by bandits.",
      grid_location: [
        6,
        6,
        0
      ],
      name: "The Forsaken Castle",
      name_prefix: "the",
      names: [
        "The Forsaken Castle"
      ],
      neighbors: {
        castle_34: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "castle_34"
        },
        neptunes_throne_room_0: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "neptunes_throne_room_0"
        }
      },
      node_id: "the_forsaken_castle_35",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    throne_1: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 19,
      contained_nodes: {
        orb_of_creation_2: {
          target_id: "orb_of_creation_2"
        }
      },
      container: true,
      container_node: {
        target_id: "neptunes_throne_room_0"
      },
      db_id: null,
      dead: false,
      desc: "That throne is where kings and queens would sit during their reign",
      drink: 0,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 0,
      locked_edge: null,
      name: "throne",
      name_prefix: "a",
      names: [
        "throne"
      ],
      node_id: "throne_1",
      object: true,
      on_use: null,
      room: false,
      size: 20,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "in",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    tithe_plate_107: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      dead: false,
      desc: "A shallow plate, but wrapped in gold, the tithe plate serves to host the devious church goers offerings.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "tithe plate",
      name_prefix: "a",
      names: [
        "tithe plate"
      ],
      node_id: "tithe_plate_107",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    torch_45: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "master_at_arms_43"
      },
      db_id: null,
      dead: false,
      desc: "The torch is stained brown from all the times it was lit.",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "torch",
      name_prefix: "a",
      names: [
        "torch"
      ],
      node_id: "torch_45",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    torn_fabric_57: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "main_hallway_1"
      },
      db_id: null,
      dead: false,
      desc: "The torn fabric is used as a cloth atop the royal dinner table.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "torn fabric",
      name_prefix: "a",
      names: [
        "torn fabric"
      ],
      node_id: "torn_fabric_57",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    town_courtroom_31: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "This is a single large room, with an aisle leading up to where the magistrate sits, which is behind a bench and podium, on either side of the aisle there are wooden pews for spectators. There are a few maps on the walls and a flag of the land, and a statue of a thief having his hands chopped off by lady justice",
      extra_desc: "This is where the magistrate hears grievances and wrongdoings of the common folk, they sue each other for wrongful deaths and witchcraft, and criminals are brought before the magistrate to be sentenced",
      grid_location: [
        6,
        3,
        0
      ],
      name: "Town Courtroom",
      name_prefix: "the",
      names: [
        "Town Courtroom"
      ],
      neighbors: {
        town_garden_30: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "town_garden_30"
        }
      },
      node_id: "town_courtroom_31",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    town_doctor_142: {
      agent: true,
      aggression: 0,
      attack_tagged_agents: [],
      blocked_by: {},
      blocking: null,
      char_type: "person",
      classes: [
        "agent"
      ],
      contain_size: 18,
      contained_nodes: {
        ink_143: {
          target_id: "ink_143"
        },
        materials_144: {
          target_id: "materials_144"
        }
      },
      container_node: {
        target_id: "wealthy_area_of_town_19"
      },
      damage: 1,
      db_id: null,
      dead: false,
      defense: 0,
      desc: "The doctor is a funny man trying to make people laugh that he is treating, he helps many people and doesn't ask for much in return, taking trades most of the time over money knowing the people don't have much.",
      dexterity: 0,
      dont_accept_gifts: false,
      followed_by: {},
      following: null,
      food_energy: 1,
      health: 2,
      is_player: false,
      max_distance_from_start_location: 1000000,
      max_wearable_items: 3,
      max_wieldable_items: 1,
      mission: "Care for people.",
      movement_energy_cost: 0,
      name: "town doctor",
      name_prefix: "a",
      names: [
        "town doctor"
      ],
      node_id: "town_doctor_142",
      num_wearable_items: 0,
      num_wieldable_items: 0,
      object: false,
      on_events: [],
      pacifist: false,
      persona: "I am the town doctor.  I have a small practice in the square in the center of the village.  The subjects line up to await my help.",
      quests: [],
      room: false,
      size: 20,
      speed: 5,
      strength: 0,
      tags: [],
      usually_npc: false
    },
    town_garden_30: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "There's a bit of dust.",
      extra_desc: [
        "Sometimes things are just what they seem. There's nothing interesting here."
      ],
      grid_location: [
        6,
        2,
        0
      ],
      name: "Town garden",
      name_prefix: "the",
      names: [
        "Town garden"
      ],
      neighbors: {
        town_courtroom_31: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "town_courtroom_31"
        },
        town_theater_29: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "town_theater_29"
        }
      },
      node_id: "town_garden_30",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    town_theater_29: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "This is a quaint theater with plush velvet seats and a beautiful red curtain. It can seat 200 people. It is decorated with mirrors and golden accents. There are posters of past plays in the lobby.",
      extra_desc: "The theater was built for the local troupe. They put on several plays a year. They also hold town meetings there. People will also rent it out for special occasions.",
      grid_location: [
        5,
        2,
        0
      ],
      name: "Town Theater",
      name_prefix: "the",
      names: [
        "Town Theater"
      ],
      neighbors: {
        town_garden_30: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "town_garden_30"
        },
        town_26: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "town_26"
        }
      },
      node_id: "town_theater_29",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    town_26: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "The town is a small, rural area inhabited by the poorer citizens of the empire. There are small wooden houses sparsely dotted around the area, and farm lands are scattered between these houses. Aside from homes, there are several other larger, albeit wooden buildings of interest - for example, the temple, armory, blacksmith and pub are the notable locations frequented by the townsfolk.",
      extra_desc: "The town was established as a small settlement well outside of the castle walls. The population consists mostly of laborsmen and poorer subsistence farmers that could not afford the houses within the castle limits. Over time, these lower class citizens settled here and built a modest, friendly town that welcomes anyone to come join them.",
      grid_location: [
        4,
        2,
        0
      ],
      name: "Town",
      name_prefix: "the",
      names: [
        "Town"
      ],
      neighbors: {
        saokras_blacksmith_shop_25: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "saokras_blacksmith_shop_25"
        },
        town_theater_29: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "town_theater_29"
        }
      },
      node_id: "town_26",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    treasure_chest_155: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "bandit_153"
      },
      db_id: null,
      dead: false,
      desc: "The treasure chest is a big rectangular box used to store treasures.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "treasure chest",
      name_prefix: "a",
      names: [
        "treasure chest"
      ],
      node_id: "treasure_chest_155",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    unsettling_forest_area_20: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1960,
      contained_nodes: {
        bandit_153: {
          target_id: "bandit_153"
        },
        fox_150: {
          target_id: "fox_150"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "The forest is actually very creepy even during the day. The trees are so tall that they block the sunlight. There is always fog in the forest which makes it very hard to see. There are a lot of mushrooms near the trees and none of them are edible",
      extra_desc: "It is believed that this forest is alive! People say that trees are moving from one place to another when nobody sees. This way hunters and other people have a hard time finding their way back. This forest never looks the same",
      grid_location: [
        2,
        2,
        0
      ],
      name: "unsettling forest area",
      name_prefix: "the",
      names: [
        "unsettling forest area"
      ],
      neighbors: {
        abandoned_farm_21: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "abandoned_farm_21"
        },
        table_area_17: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "table_area_17"
        }
      },
      node_id: "unsettling_forest_area_20",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    unused_chamber_33: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 2000,
      contained_nodes: {},
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "There's a bit of dirt.",
      extra_desc: [
        "Sometimes things are just what they seem. There's nothing interesting here."
      ],
      grid_location: [
        6,
        5,
        0
      ],
      name: "Unused chamber",
      name_prefix: "the",
      names: [
        "Unused chamber"
      ],
      neighbors: {
        outside_castle_32: {
          examine_desc: null,
          label: "a path to the west",
          locked_edge: null,
          target_id: "outside_castle_32"
        }
      },
      node_id: "unused_chamber_33",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    wall_hanging_55: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "serving_boy_51"
      },
      db_id: null,
      dead: false,
      desc: "The wall hanging shows a deep history imbedded in to it.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "wall hanging",
      name_prefix: "a",
      names: [
        "wall hanging"
      ],
      node_id: "wall_hanging_55",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    water_pail_106: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "pail_105"
      },
      db_id: null,
      dead: false,
      desc: "The pail had rust on it's handle and there was a hole rusted through the bottom.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "water pail",
      name_prefix: "a",
      names: [
        "water pail"
      ],
      node_id: "water_pail_106",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    wealthy_area_of_town_19: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 1959,
      contained_nodes: {
        milk_man_145: {
          target_id: "milk_man_145"
        },
        scrap_of_fur_141: {
          target_id: "scrap_of_fur_141"
        },
        town_doctor_142: {
          target_id: "town_doctor_142"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "A new section of town, new stone buildings and with fresh paint and clean installations. It looks like an old city of rich bankers and guilds of merchants.",
      extra_desc: "This city was once a garrison for the King's soldiers but in times of peace has become the commerce hub of the region. You can see some military installations but they are old and unused, relics of an earlier time.installations",
      grid_location: [
        1,
        1,
        0
      ],
      name: "Wealthy area of town",
      name_prefix: "the",
      names: [
        "Wealthy area of town"
      ],
      neighbors: {
        abandoned_farm_21: {
          examine_desc: null,
          label: "a path to the east",
          locked_edge: null,
          target_id: "abandoned_farm_21"
        },
        table_area_17: {
          examine_desc: null,
          label: "a path to the south",
          locked_edge: null,
          target_id: "table_area_17"
        }
      },
      node_id: "wealthy_area_of_town_19",
      object: false,
      room: true,
      size: 2000,
      surface_type: "in"
    },
    whip_40: {
      agent: false,
      classes: [
        "object",
        "wieldable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "personal_rooms_0"
      },
      db_id: null,
      dead: false,
      desc: "The whip is black and long, the ends stained with some red substance.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "whip",
      name_prefix: "a",
      names: [
        "whip"
      ],
      node_id: "whip_40",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: true
    },
    wizards_quarters_3: {
      agent: false,
      classes: [
        "room"
      ],
      contain_size: 100000,
      contained_nodes: {
        chair_5: {
          target_id: "chair_5"
        },
        cupboard_11: {
          target_id: "cupboard_11"
        },
        lavish_desk_piled_high_wi6: {
          target_id: "lavish_desk_piled_high_wi6"
        },
        shelf_4: {
          target_id: "shelf_4"
        }
      },
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      desc: "Dark and musty, the Wizard's Quarters are filled with ancient tomes and mysterious items.  Scrolls and jars of mysterious reagents line the walls of the Wizard's Quarters, and magical lights flicker with a mysterious green flame.",
      extra_desc: "Dark and musty, the Wizard's Quarters are filled with ancient tomes and mysterious items.  Scrolls and jars of mysterious reagents line the walls of the Wizard's Quarters, and magical lights flicker with a mysterious green flame.",
      grid_location: [
        1,
        -1,
        0
      ],
      name: "Wizard's Quarters",
      name_prefix: "the",
      names: [
        "Wizard's Quarters"
      ],
      neighbors: {
        dungeon_within_a_castle_2: {
          examine_desc: null,
          label: "a path to the north",
          locked_edge: null,
          target_id: "dungeon_within_a_castle_2"
        }
      },
      node_id: "wizards_quarters_3",
      object: false,
      room: true,
      size: 1,
      surface_type: "in"
    },
    wizards_tome_12: {
      agent: false,
      classes: [
        "object"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "cupboard_11"
      },
      db_id: null,
      dead: false,
      desc: "This book describes many sundry spells and incantations in arcane language. Amongst them, it speaks of the orb of creation, a incredibly powerful device that when wielded and chanting such words as \"creo device stone\" one can create a stone! \"creo loci cave\" one can create a cave! or even \"creo creatura dog\" one can summon a living dog!",
      drink: 0,
      equipped: null,
      food: 0,
      food_energy: 1,
      gettable: 1,
      locked_edge: null,
      name: "wizard's tome",
      name_prefix: "a",
      names: [
        "wizard's tome"
      ],
      node_id: "wizards_tome_12",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "in",
      value: 1,
      wearable: 0,
      wieldable: 0
    },
    wood_is_gathered_to_make_113: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 1,
      contained_nodes: {
        candle_114: {
          target_id: "candle_114"
        },
        key_115: {
          target_id: "key_115"
        }
      },
      container: true,
      container_node: {
        target_id: "pine_tree_graveyard_13"
      },
      db_id: null,
      dead: false,
      desc: "The wood lay scorched on the ground, and warm to the touch.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "wood that is gathered to make fire",
      name_prefix: "a",
      names: [
        "wood is gathered to make fire"
      ],
      node_id: "wood_is_gathered_to_make_113",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    wooden_bed_126: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 30,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "VOID"
      },
      db_id: null,
      dead: false,
      desc: "A simple wooden rectangle with a grid of interwoven ropes to support a mattress.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "wooden bed",
      name_prefix: "a",
      names: [
        "wooden bed"
      ],
      node_id: "wooden_bed_126",
      object: true,
      on_use: null,
      room: false,
      size: 30,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    wooden_cross_117: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "priest_116"
      },
      db_id: null,
      dead: false,
      desc: "The wooden cross is faded in color from being worn too much by the priest",
      drink: false,
      equipped: true,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "wooden cross",
      name_prefix: "a",
      names: [
        "wooden cross"
      ],
      node_id: "wooden_cross_117",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    },
    wooden_spit_125: {
      agent: false,
      classes: [
        "container",
        "object"
      ],
      contain_size: 3,
      contained_nodes: {},
      container: true,
      container_node: {
        target_id: "half_wild_cat_123"
      },
      db_id: null,
      dead: false,
      desc: "The wooden spit shows signs of repeated use.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "wooden spit",
      name_prefix: "a",
      names: [
        "wooden spit"
      ],
      node_id: "wooden_spit_125",
      object: true,
      on_use: null,
      room: false,
      size: 4,
      stats: {
        damage: 0,
        defense: 0
      },
      surface_type: "on",
      value: 1,
      wearable: false,
      wieldable: false
    },
    worn_quilt_38: {
      agent: false,
      classes: [
        "object",
        "wearable"
      ],
      contain_size: 0,
      contained_nodes: {},
      container: false,
      container_node: {
        target_id: "expensive_carpet_37"
      },
      db_id: null,
      dead: false,
      desc: "the quilt is old and worn out.",
      drink: false,
      equipped: null,
      food: false,
      food_energy: 0,
      gettable: true,
      locked_edge: null,
      name: "worn quilt",
      name_prefix: "a",
      names: [
        "worn quilt"
      ],
      node_id: "worn_quilt_38",
      object: true,
      on_use: null,
      room: false,
      size: 1,
      stats: {
        attack: 1
      },
      surface_type: "on",
      value: 1,
      wearable: true,
      wieldable: false
    }
  },
  objects: [
    "apple_tree_13",
    "apron_133",
    "bathroom_pot_61",
    "bedding_65",
    "bell_53",
    "blacksmiths_hammer_128",
    "blanket_42",
    "block_and_tackle_111",
    "bottle_of_wine_164",
    "bow_and_arrows_82",
    "bow_81",
    "bowl_of_fruit_94",
    "broken_glass_36",
    "bucket_for_eliminating_wa87",
    "candle_114",
    "candy_93",
    "cannon_96",
    "cargo_100",
    "chair_5",
    "chamber_pot_60",
    "chamberpot_152",
    "chicken_69",
    "clothes_made_of_various_p138",
    "computer_48",
    "cookpot_131",
    "corn_137",
    "cup_134",
    "cupboard_11",
    "dexteritate_scroll_9",
    "dress_88",
    "embalming_equipment_90",
    "expensive_carpet_37",
    "feather_fountain_pen_112",
    "finest_silk_and_velvet_158",
    "fish_wrap__or_butcher_pap85",
    "fishing_rod_1",
    "flower_pot_75",
    "food_tray_119",
    "fresh_dry_house_shoes_72",
    "fresh_red_paint_70",
    "giant_club_46",
    "grappling_hook_56",
    "gray_stone_78",
    "hair_brush_50",
    "hand_plow_109",
    "harness_154",
    "hatchet_91",
    "heavy_blanket_103",
    "hefty_rock_14",
    "homestead_equipment_129",
    "horse_tack_89",
    "huge_cast_iron_pot_62",
    "ink_jar_156",
    "ink_well_64",
    "ink_143",
    "key_115",
    "lance_110",
    "large_earthenware_jug_of_74",
    "large_pile_of_hay_73",
    "lavish_desk_piled_high_wi6",
    "lush_green_vegetation_63",
    "luxurious_bedding_66",
    "mace_162",
    "magical_crystal_127",
    "magical_lights_124",
    "magnitudo_scroll_10",
    "map_of_the_kingdom_102",
    "materials_144",
    "meat_161",
    "metal_bucket_148",
    "metal_meal_tray_120",
    "milk_146",
    "moldy_bread_159",
    "mortem_scroll_8",
    "muddy_area_0",
    "mug_of_mead_147",
    "mystical_necklace_with_a_49",
    "name_placard_59",
    "old_armor_170",
    "old_broom_97",
    "old_prayer_books_54",
    "old_sun_bleached_sailclot44",
    "orb_of_creation_2",
    "ornate_goblet_41",
    "pail_105",
    "paper_101",
    "pond_0",
    "prayer_book_118",
    "priceless_painting_52",
    "primitive_fishing_pole_92",
    "rare_wood_from_a_tree_tha166",
    "red_brick_167",
    "ritual_dagger_39",
    "ritual_knife_77",
    "roasting_meat_132",
    "rock_104",
    "rotting_meat_122",
    "salt_168",
    "sapphire_71",
    "scrap_of_fur_141",
    "scroll_7",
    "shelf_4",
    "shield_47",
    "shovel_1",
    "sleet_121",
    "small_bucket_86",
    "small_crucifix_84",
    "small_metal_bucket_149",
    "spoon_135",
    "suit_of_armor_79",
    "sword_of_the_guards_151",
    "sword_80",
    "tent_67",
    "throne_1",
    "tithe_plate_107",
    "torch_45",
    "torn_fabric_57",
    "treasure_chest_155",
    "wall_hanging_55",
    "water_pail_106",
    "whip_40",
    "wizards_tome_12",
    "wood_is_gathered_to_make_113",
    "wooden_bed_126",
    "wooden_cross_117",
    "wooden_spit_125",
    "worn_quilt_38"
  ],
  rooms: [
    "abandoned_farm_21",
    "castle_34",
    "central_garden_4",
    "countryside_23",
    "disposal_area_16",
    "dungeon_within_a_castle_2",
    "dungeon_1",
    "empty_storage_room_27",
    "entrance_to_a_cave_0",
    "entrance_to_the_pine_tree15",
    "fish_market_28",
    "main_entrance_7",
    "main_gate_8",
    "main_graveyard_9",
    "main_hallway_1",
    "main_house_3",
    "main_street_6",
    "modest_living_area_18",
    "neptunes_throne_room_0",
    "outside_castle_32",
    "personal_quarters_2",
    "personal_rooms_0",
    "picnic_area_14",
    "pine_tree_graveyard_13",
    "reception_area_12",
    "saokras_blacksmith_shop_25",
    "shop_in_bazaar_24",
    "small_graveyard_10",
    "small_hut_11",
    "stretch_of_road_5",
    "table_area_17",
    "the_forest_22",
    "the_forsaken_castle_35",
    "town_courtroom_31",
    "town_garden_30",
    "town_theater_29",
    "town_26",
    "unsettling_forest_area_20",
    "unused_chamber_33",
    "wealthy_area_of_town_19",
    "wizards_quarters_3"
  ]
}


const DummyWorlds = [
    SimpleWorld,
    SimpleWorld2,
    ComplexWorld1
]
  
export default DummyWorlds; 