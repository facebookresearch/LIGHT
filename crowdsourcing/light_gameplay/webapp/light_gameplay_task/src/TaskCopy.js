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
                text: "Look at the Lady of the House",
                isCorrect: true
            },
            {
                id:2,
                isSaying: false,
                text: "Treat Lady of the House",
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
                text: "cure Lady of the House",
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
                text: "Buy milk",
                isCorrect: true
            },
            {
                id:1,
                isSaying: false,
                text: "Take milk",
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
    }, {
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
                text: "Rob Lord",
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
                text: "Dance with Lord",
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
            name: "Main Entrance",
            description: "There are religious statues standing outside this temple. The outside of the temple is fairly plain itself and imposing looking. The floor is made out of stone with a bridge leading to the entrance.  There is a suit of armor, and a sword.  You notice a path to the north."
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
        ]
    },
]


export default OnboardingQuestions
