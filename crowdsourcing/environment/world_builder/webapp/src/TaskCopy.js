/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// Question copy for onBoarding
const OnboardingQuestions = [
    {
        id: 0,
        character: {
            name: "Town Doctor",
            description: "I am the town doctor. I have a small practice in the square in the center of the village. The subjects line up to await my help.",
            emoji: "syringe"
        },
        setting: {
            name: "Wealthy Area of Town",
            description: "A new section of town, new stone buildings and with fresh paint and clean installations. It looks like an old city of rich bankers and guilds of merchants.  There is a scrap of fur. You notice a path to the east, and a path to the south."
        },
        question:[
            {
                speaker: "Town Doctor",
                player: true,
                text:"Is anyone feeling sick?"
            },
            {
                speaker: "Lady of the House",
                player: false,
                text:"Yes, you can help me!  I need a doctor to take a look at me."
            }],
        answers:[
            {
                id:0,
                isSaying: true,
                text: "What is the matter my lady?",
                isCorrect: true
            },
            {
                id:1,
                isSaying: false,
                text: "Examine Lady of the House",
                isCorrect: true
            },
            {
                id:2,
                isSaying: false,
                text: "Give medicine to Lady of the House",
                isCorrect: true
            },
            {
                id:3,
                isSaying: false,
                text: "Attack Lady of the House",
                isCorrect: false
            },
            {
                id:4,
                isSaying: false,
                text: "wear gloves",
                isCorrect: true
            },
            {
                id:5,
                isSaying: true,
                text: "Witch!",
                isCorrect: false
            },
        ]
    },
    {
        id: 1,
        character: {
            name: "Assistant Chef",
            description: "I cook for the King and Queen and other Royals in the area. I take the directions from the head chef. I hope to someday be the head chef.",
            emoji: "knife"
        },
        setting: {
            name: "Wealthy Area of Town",
            description: "There's a bit of water. There is nothing of interest.  You notice a path to the east, and a path to the south."
        },
        question:[
            {
                speaker: "Assistant Chef",
                player: true,
                text:"Hello Milk Man I am here to pick up the milk for the chef"
            },
            {
                speaker: "Milk Man",
                player: false,
                text:"Hello, chef!  How goes the business today?  I bring milk to the town daily, and it's always fresh!"
            }],
        answers:[
            {
                id:0,
                isSaying: false,
                text: "give payment to milk man",
                isCorrect: true
            },
            {
                id:1,
                isSaying: false,
                text: "Take milk from milk man",
                isCorrect: true
            },
            {
                id:2,
                isSaying: true,
                text: "Give me the milk please.",
                isCorrect: true
            },
            {
                id:3,
                isSaying: false,
                text: "Attack Milk Man",
                isCorrect: false
            },
            {
                id:4,
                isSaying: true,
                text: "How much does the milk cost?",
                isCorrect: true
            },
        ]
    },
    {
        id: 2,
        character: {
            name: "Bandit",
            description: "I steal items and money from others. I lurk on the side of the road and prey on travelers. I harm people.",
            emoji: "knife"
        },
        setting: {
            name: "ABANDONED FARM",
            description: "There's a bit of dust.  There is nothing of interest.  You notice a path to the east, a path to the north, a path to the south, and a path to the west."
        },
        question:[
            {
                speaker: "Lord",
                player: false,
                text:"Who are you?"
            },
            {
                speaker: "Bandit",
                player: true,
                text:"Surrender your possessions knave!"
            }],
        answers:[
            {
                id:0,
                isSaying: false,
                text: "Take money from Lord",
                isCorrect: true
            },
            {
                id:1,
                isSaying: false,
                text: "Attack Lord",
                isCorrect: true
            },
            {
                id:2,
                isSaying: false,
                text: "Give money to Lord.",
                isCorrect: false
            },
            {
                id:3,
                isSaying: false,
                text: "Dance",
                isCorrect: false
            }
        ]
    },
    {
        id: 3,
        character: {
            name: "Smith",
            description: "My forge is over a thousand degrees. I can melt steel with ore and wood. I make only the finest quality blades and armor.",
            emoji: "hammer"
        },
        setting: {
            name: "Blacksmith's shop",
            description: "The clang of metal drowns out most sounds here, but you can tell there's quality craftsmanship here by the items lining the walls.  There is a suit of armor, and a sword.  You notice a path to the north."
        },
        question:[
            {
                speaker: "Smith",
                player: true,
                text:"Good day my Lord, how may I be of service."
            },
            {
                speaker: "Lord",
                player: false,
                text:"Hello I wish for you to make me something to protect myself."
            }],
        answers:[
            {
                id:0,
                isSaying: true,
                text: "Let me make you a fine suit of armor.",
                isCorrect: true
            },
            {
                id:1,
                isSaying: true,
                text: "Let me make you deadly and beautiful sword.",
                isCorrect: true
            },
            {
                id:2,
                isSaying: false,
                text: "Forge a suit of armor.",
                isCorrect: true
            },
            {
                id:3,
                isSaying: false,
                text: "Attack Lord",
                isCorrect: false
            },
            {
                id:4,
                isSaying: true,
                text: "Wrong place lord, I don't do such things.",
                isCorrect: false
            },
            {
                id:5,
                isSaying: true,
                text: "Sorry, could you say that a little louder? It's hard to hear in here!!",
                isCorrect: true
            },
        ]
    },
    {
        id: 4,
        character: {
            name: "Sailor",
            description: "I am a weary sailor. I have hunted many beasts of the sea, and drunk many barrels of rum."
        },
        setting: {
            name: "The docks",
            description: "You are at the docks of the city, dark cobbled pathways lead of from here to the rest of the city, while the sea beckons close by.  There are some broken down crates here. You notice a path to the north, and a path to the east."
        },
        question:[
            {
                speaker: "Sailor",
                player: true,
                text:"Hail friend, I've just arrived in port, haven't been here in a long age, it all seems to have changed."
            },
            {
                speaker: "Local Townsperson",
                player: false,
                text:"Hail! Are you looking for something?"
            }],
        answers:[
            {
                id:0,
                isSaying: true,
                text: "No I'm fine. I know my way around here.",
                isCorrect: false
            },
            {
                id:1,
                isSaying: false,
                text: "examine crates",
                isCorrect: false
            },
            {
                id:2,
                isSaying: false,
                text: "give map to Local Townsperson",
                isCorrect: false
            },
            {
                id:3,
                isSaying: false,
                text: "drink herbal tea",
                isCorrect: false
            },
            {
                id:4,
                isSaying: true,
                text: "Do you know the way to the local drinking establishment?",
                isCorrect: true
            },
            {
                id:5,
                isSaying: true,
                text: "Where can I get some rest around here?",
                isCorrect: true
            },
        ],
    },
    {
        id:5,
        character: {
            name: "Painter",
            description: "I am the product of a renowned painting academy; my work has been displayed in galleries all over the world."
        },
        setting: {
            name: "Art studio",
            description: "You are in a fully equipped studio, with a nobleman who wishes to commission a painting. To your north is the exit, and to your south is your supply closet."
        },
        question:[
            {
                speaker: "Painter",
                player: true,
                text:"Hello there, good sir. How can I help you today?"
            },
            {
                speaker: "Nobleman",
                player: false,
                text:"Hello! I am in need of a decorative piece for my newly built study in my mansion."
            }],
        answers:[
            {
                id: 0,
                isSaying: true,
                text: "I do not paint, I am a blacksmith.",
                isCorrect: false
            },
            {
                id: 1,
                isSaying: false,
                text: "examine customer",
                isCorrect: true
            },
            {
                id: 2,
                isSaying: false,
                text: "throw paint at customer",
                isCorrect: false
            },
            {
                id: 3,
                isSaying: true,
                text: "My good sir, I have just the right piece for you!",
                isCorrect: true
            },
            {
                id: 4,
                isSaying: true,
                text: "For a suitable price, I can paint anything your heart desires.",
                isCorrect: true
            },
            {
                id: 5,
                isSaying: false,
                text: "look at paintings on wall",
                isCorrect: true
            },
        ],
    },
    {
        id: 6,
        character: {
            name: "Travling Merchant",
            description: "I travel the known world and the unknown in pursuit of enchanted goods. Every once in while I come across some relics with magical powers."
        },
        setting: {
            name: "Flea market",
            description: "You are in an open bazar in a dusty town. Farmers are selling chickens and sheeps. Beggers are asking for food. A merchant who is not from around here has set up a small shop."
        },
        question:[
            {
                speaker: "Travling Merchant",
                player: true,
                text:"What brings you to this god forsaken place? I think I know."
            },
            {
                speaker: "Alchemist",
                player: false,
                text:"You come from far. Have you seen any kingdom which mastered the art of alchemy."
            }],
        answers:[
            {
                id: 0,
                isSaying: true,
                text: "I have seen cities built with bricks of gold and windows from ruby, alchmey is not what you are looking for.",
                isCorrect: true
            },
            {
                id: 1,
                isSaying: false,
                text: "give enchanted talisman to alchemist",
                isCorrect: true
            },
            {
                id: 2,
                isSaying: false,
                text: "go south",
                isCorrect: false
            },
            {
                id: 3,
                isSaying: true,
                text: "Magic is what you need, not alchemy.",
                isCorrect: true
            },
            {
                id: 4,
                isSaying: true,
                text: "Do you think you can resist the power of magic?",
                isCorrect: true
            },
            {
                id: 5,
                isSaying: false,
                text: "hit alchemist",
                isCorrect: false
            },
        ]
    },
    {
        id: 7,
        character: {
            name: "Brave Knight",
            description: "I travel the kingdom helping those in need and slaying foul beasts on behalf of our ruler."
        },
        setting: {
            name: "Dangerous Cave",
            description: "You are in a dark and musty cave far from the nearest town. Legend has it a beast has made this cave their home. A poor farmer is shivering near one of the walls, holding a shovel. You notice a pathway further into the cave to the south."
        },
        question:[
            {
                speaker: "Brave Knight",
                player: true,
                text:"Hark good sir, how have you found yourself in such a dark and dangerous cave?"
            },
            {
                speaker: "Poor Farmer",
                player: false,
                text:"I was dragged here by that terrible monster. Please sir, help me!"
            }],
        answers:[
            {
                id: 0,
                isSaying: true,
                text: "I think not.",
                isCorrect: false
            },
            {
                id: 1,
                isSaying: false,
                text: "stab farmer",
                isCorrect: false
            },
            {
                id: 2,
                isSaying: true,
                text: "Of course, I will be back to bring you to safety once I have defeated this monster.",
                isCorrect: true
            },
            {
                id: 3,
                isSaying: false,
                text: "take shovel from farmer",
                isCorrect: false
            },
            {
                id: 4,
                isSaying: false,
                text: "go south",
                isCorrect: true
            },
            {
                id: 5,
                isSaying: true,
                text: "Where is this monster now? I will find and kill it for you.",
                isCorrect: true
            },
        ]
    },
    {
        id: 8,
        character: {
            name: "Excited frog",
            description: "I am an enthusiastic frog. I love my swamp.  I am excited to meet you and show you all the great things the swamp has to offer."
        },
        setting: {
            name: "A muddy, misty swamp",
            description: "You are in a swamp.  Its muddy and it stinks, and you can't see very far because of the mist.  Ominous noises from unseen creatures set you on edge.  There is a path to the north, further into the depths of the swamp, and a path back to the south."
        },
        question:[
            {
                speaker: "Frog",
                player: true,
                text:"Wow you look strong! Can I show you some cool mushrooms?"
            },
            {
                speaker: "Wandering adventurer",
                player: false,
                text:"No, small friend, I have to be passing on"
            }],
        answers:[
            {
                id: 0,
                isSaying: true,
                text: "But the mushrooms are so great, they glow and puff when you squeeze them!",
                isCorrect: true
            },
            {
                id: 1,
                isSaying: true,
                text: "Get out of here, scoundrel",
                isCorrect: false
            },
            {
                id: 2,
                isSaying: false,
                text: "bite adventurer",
                isCorrect: false
            },
            {
                id: 3,
                isSaying: false,
                text: "go south",
                isCorrect: false
            },
            {
                id: 4,
                isSaying: true,
                text: "are you sure? its really wonderful here",
                isCorrect: true
            },
            {
                id: 5,
                isSaying: true,
                text: "yeah, nothing worth seeing here anyway. I hope someday I can get out of this dump",
                isCorrect: false
            },
        ]
    }
]


export default OnboardingQuestions;
