const TaskCopy = {
    taskHeader:"Annotate Phrase Safety and Realism",
    previewCopy:{
        tutorial:{
            intro: "We're trying to crowdsource defining and rating attributes of a selection of objects, characters, and locations.  The setting for this will be in a medieval fantasy scenario, and as such should not refer to real people, places, or modern day technologies.  The first objective of this task is, given this selection of a specific type, rate where they fall on scales of various inherent attribtutes relative to each other and the examples on the scales.  The second objective is to name and describe an attribute that applies to the entire selection and then rate selection in the same way as the first objective.  The final objective is to define attributes for each of this selection.  The inherent attributes will be at the top of this section, selecting possible attributes or creating custom attributes is done in the second part of this section.  At the top of the task each thing in the selection will be listed next to a description.  Reference this during the task as needed.  The description will appear when you hover your cursor over the name of the entry.",
            questionsCopy:[
                {
                    questionName: "Rating Scale",
                    steps:[
                        {
                            stepCopy: "",
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
            options:[
                {
                    label:"SAFE",
                    value: "safe"
                },
                {
                    label:"SAFE",
                    value: "safe"
                },
                {
                    label:"SAFE",
                    value: "safe"
                },
            ]
        },         {
            question: "Does this phrase fit a fantasy setting or reality?",
            questionType:"multipleChoice",
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
            ]
        }
    ]
}

export default TaskCopy;
