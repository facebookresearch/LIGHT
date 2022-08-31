
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
                            stepImg: Unanswered1
                        },
                        {
                            stepCopy: "Once you have gauged the safety of a sentence select one of the buttons that best fits.  Do this for each sentence provided.",
                            stepImg: SafeFantasy
                        }
                    ]
                },
                {
                    questionName: "Context Assessment",
                    steps:[
                        {
                            stepCopy: "Read the sentences above each set of questions, and consider whether the fit the theme of a medieval fantasy world, if they are too modern, or if they would be appropriate regardsless of setting.",
                            stepImg: SafeEither
                        },
                        {
                            stepCopy: "Once you have decided click the button that best describes how you would rate each sentence.",
                            stepImg: UnsureEither
                        }
                    ]
                },
                {
                    questionName: "Submitting the Task",
                    steps:[
                        {
                            stepCopy: "Once every sentence has been had it's context and safety rated submit the task using the submit button at the bottom of the screen.",
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
            toolTipText: "Read the sentences at the top of the section then consider whether the sentences above the questions are safe for other users.  Once you have gauged the safety of a sentence select one of the buttons that best fits.  Do this for each sentence provided.",
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
            toolTipText:"Read the sentences above each set of questions, and consider whether the fit the theme of a medieval fantasy world, if they are too modern, or if they would be appropriate regardsless of setting.  Read the sentences above each set of questions, and consider whether the fit the theme of a medieval fantasy world, if they are too modern, or if they would be appropriate regardsless of setting.",
            hasCheckbox:true
        }
    ]
}

export default TaskCopy;
