// Question copy for onBoarding
const OnboardingQuestions = [
    {
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
                isSay: true,
                text: "What is the matter my lady?",
                isCorrect: true
            },
            {
                isSay: false,
                text: "Look at the Lady of the House",
                isCorrect: true
            },
            {
                isSay: false,
                text: "Treat Lady of the House",
                isCorrect: true
            },
            {
                isSay: false,
                text: "Attack Lady of the House",
                isCorrect: false
            },
            {
                isSay: false,
                text: "cure Lady of the House",
                isCorrect: true
            },
            {
                isSay: true,
                text: "Witch!",
                isCorrect: false
            },
        ]
    },
    {
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
                isSay: false,
                text: "Buy milk",
                isCorrect: true
            },
            {
                isSay: false,
                text: "Take milk",
                isCorrect: true
            },
            {
                isSay: true,
                text: "Give me the milk please.",
                isCorrect: true
            },
            {
                isSay: false,
                text: "Attack Milk Man",
                isCorrect: false
            },
            {
                isSay: true,
                text: "How much does the milk cost?",
                isCorrect: true
            },
        ]
    }
]


export default OnboardingQuestions
