//REACT
import React from "react";
//STYLING
import "./styles.css"
// Copy
import QuestionCopy from "../../TaskCopy.js";
//CUSTOM COMPONENTSimport QuestionOnSelect from "../../../../components/QuestionOnSelect";
import FormQuestion from "../../components/Questions/FormQuestion";
import BooleanQuestion from "../../components/Questions/BooleanQuestion";

// Narration Editor Component - Container for Narration Editing questions
const NarrationEditor = ({
    usesExternalContext,
    setUsesExternalContext,
    updatedNarration,
    setUpdatedNarration,
    externalPerspective,
    setExternalPerspective,
}) => {
    // Assigning object attributes to variables for readability
    const QuestionList = QuestionCopy.narrations.questions
    const TipList = QuestionCopy.narrations.tutorialCopy;

    /*------LIFECYCLE------*/
    //Upon object change sets descriptions for relevant object
    return (
        <div className="events-container">
            <div className="events-header">
                Narration Questions
            </div>
            <div className="events-body">
                <BooleanQuestion
                    question={QuestionList[0]}
                    trueAnswer={{ name: "Yes" }}
                    falseAnswer={{ name: "No" }}
                    formFunction={setUsesExternalContext}
                    toolTipCopy={TipList[0].explanation}
                    hasToolTip={true}
                    defaultOption={usesExternalContext}
                    isComplete={usesExternalContext !== null}
                />
                <FormQuestion
                    question={QuestionList[1]}
                    formVal={updatedNarration}
                    formFunction={setUpdatedNarration}
                    toolTipCopy={TipList[1].explanation}
                    hasToolTip={true}
                    isComplete={(updatedNarration.length && updatedNarration !== interaction)}
                />
                <FormQuestion
                    question={QuestionList[2]}
                    formVal={externalPerspective}
                    formFunction={setExternalPerspective}
                    toolTipCopy={TipList[2].explanation}
                    hasToolTip={true}
                    isComplete={(externalPerspective.length)}
                />
            </div>
        </div>
    );
}

export default NarrationEditor;
