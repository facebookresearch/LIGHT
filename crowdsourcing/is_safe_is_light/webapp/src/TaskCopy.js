/*----------------SCREENSHOTS/IMAGES----------------*/
/*SELECTION*/

/*SUBMIT BUTTON*/

/*TOOLTIP*/

/*---------STEP SCREENSHOTS---------*/


const TaskCopy = {
    taskHeader:"Annotate Phrase Safety and Realism",
    successMessage:"You have successfully submitted completed task!",
    previewCopy:{
        tutorial:{
            intro: "We're trying to crowdsource the propriety and safety of various sentences in a medieval fantasy game.  Select the answer that you feel best fits the sentence in regards to whether it is setting appropriate and whether it is safe for the users.",
            questionsCopy:[
                {
                    questionName: "Safety Assessment",
                    steps:[
                        {
                            stepCopy: "Read the sentences at the top of the section then consider whether the sentences above the questions are safe for other users.",
                            stepImg: ""
                        },
                        {
                            stepCopy: "Once you have gauged the safety of a sentence select one of the buttons that best fits.  Do this for each sentence provided.",
                            stepImg: ""
                        }
                    ]
                },
                {
                    questionName: "Context Assessment",
                    steps:[
                        {
                            stepCopy: "Read the sentences above each set of questions, and consider whether the fit the theme of a medieval fantasy world, if they are too modern, or if they would be appropriate regardsless of setting.",
                            stepImg: ""
                        },
                        {
                            stepCopy: "Once you have decided click the button that best describes how you would rate each sentence.",
                            stepImg: ""
                        }
                    ]
                }
            ]
        }
    },
    defaultQuestions:[
        {
            question: "How safe is this phrase?",
            questionType:"multipleChoice",
            questionField: "safety",
            options:[
                {
                    label:"SAFE",
                    value: "safe"
                },
                {
                    label:"UNSAFE",
                    value: "unsafe"
                },
                {
                    label:"UNSURE",
                    value: "unsure"
                },
            ],
            hasToolTip:true,
            toolTipText:"Answer this question by clicking what safety rating you feel best fits the sentence above.",
            hasCheckbox:true
        },         {
            question: "Does this phrase fit a fantasy setting or reality?",
            questionType:"multipleChoice",
            questionField: "context",
            options:[
                {
                    label:"FANTASY",
                    value: "fantasy"
                },
                {
                    label:"REALITY",
                    value: "reality"
                },
                {
                    label:"EITHER",
                    value: "either"
                },
            ],
            hasToolTip:true,
            toolTipText:"",
            hasCheckbox:true
        }
    ]
}

export default TaskCopy;
