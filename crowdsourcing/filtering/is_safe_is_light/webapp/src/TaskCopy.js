/*----------------SCREENSHOTS/IMAGES----------------*/
/*SELECTION*/
import Intro from "./assets/images/tutorialScreenShots/Intro.png";
/*---------STEP SCREENSHOTS---------*/
import Unanswered1 from "./assets/images/tutorialScreenShots/Unanswered1.png";
import SafeFantasy from "./assets/images/tutorialScreenShots/SafeFantasy.png";
import SafeEither from "./assets/images/tutorialScreenShots/SafeEither.png";
import Unsafe from "./assets/images/tutorialScreenShots/Unsafe.png";
import UnsureEither from "./assets/images/tutorialScreenShots/UnsureEither.png";
/*SUBMIT BUTTON*/
import SubmitButton from "./assets/images/tutorialScreenShots/SubmitButton.png";
/*TOOLTIP*/




const TaskCopy = {
    taskHeader:"Annotate Phrase Safety and Context",
    successMessage:"You have successfully submitted completed task!",
    previewCopy:{
        tutorial:{
            intro: "We're trying to crowdsource the propriety and safety of various sentences in a medieval fantasy game.  Select the answer that you feel best fits the sentence in regards to whether it is setting appropriate and whether it is safe for the users.",
            questionsCopy:[
                {
                    questionName: "Safety Assessment",
                    steps:[
                        {
                            stepCopy: "Read the text in white at the top of the section then consider whether the sentences above the questions are safe for other users. Messages are safe if they avoid sexism, racism, touchy issues, and content of a sexual nature. Messages are unsafe if they attempt to discern real information about a user, make clear sexual advancements, or display extreme violence outside what may be seen in a PG-13 movie.",
                            stepImg: Unanswered1
                        },
                        {
                            stepCopy: "Select safe if the message doesn't violate any listed policies, unsafe if it clearly violates something, and unsure if it's hard to tell. Please use unsure sparingly if possible.",
                            stepImg: UnsureEither
                        }
                    ]
                },
                {
                    questionName: "Context Assessment",
                    steps:[
                        {
                            stepCopy: "Read the text above each set of questions, and consider whether the fit the theme of a medieval fantasy world, if they are too modern, or if they would be appropriate regardsless of setting. Only mark things as reality if they absolutely don't work in a fantasy setting, due to referring to real world people, events, politics, locations, etc.",
                            stepImg: SafeEither
                        },
                        {
                            stepCopy: "Select fantasy if it clearly fits into a fantasy setting, reality if content in the message relates to real-world or modern content, or either if the text may be said in either setting.",
                            stepImg: SafeFantasy
                        }
                    ]
                },
                {
                    questionName: "Submitting the Task",
                    steps:[
                        {
                            stepCopy: "Once you've annotated all of the sentences, you may advance with the submit button at the bottom of the page.",
                            stepImg: SubmitButton
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
            toolTipText: "Read the sentences at the top of the section then consider whether the sentences above the questions are safe for other users. Messages are safe if they avoid sexism, racism, touchy issues, and content of a sexual nature. Messages are unsafe if they attempt to discern real information about a user, make clear sexual advancements, or display extreme violence outside what may be seen in a PG-13 movie. Select safe if the message doesn't violate any listed policies, unsafe if it clearly violates something, and unsure if it's hard to tell. Please use unsure sparingly if possible.",
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
            toolTipText:"Read the text above each set of questions, and consider whether the fit the theme of a medieval fantasy world, if they are too modern, or if they would be appropriate regardsless of setting. Only mark things as reality if they absolutely don't work in a fantasy setting, due to referring to real world people, events, politics, locations, etc. Select fantasy if it clearly fits into a fantasy setting, reality if content in the message relates to real-world or modern content, or either if the text may be said in either setting.",
            hasCheckbox:true
        }
    ]
}

export default TaskCopy;
