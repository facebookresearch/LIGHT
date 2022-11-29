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
    interaction,
    baseExternalPerspective,
    usesExternalContext,
    setUsesExternalContext,
    updatedNarration,
    setUpdatedNarration,
    externalPerspective,
    setExternalPerspective,
}) => {
    // Assigning object attributes to variables for readability
    const QuestionList = QuestionCopy.narration.questions
    const TipList = QuestionCopy.narration.tutorialCopy;

    /*------LIFECYCLE------*/
    //Upon object change sets descriptions for relevant object
    return (
        <div className="narration-container">
            <div className="narration-header">
                Narration Questions
            </div>
            <div className="narration-body">
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
                    placeholder={interaction}
                    formVal={updatedNarration}
                    formFunction={setUpdatedNarration}
                    toolTipCopy={TipList[1].explanation}
                    hasToolTip={true}
                    isComplete={(updatedNarration.length && updatedNarration !== interaction)}
                />
                <FormQuestion
                    question={QuestionList[2]}
                    placeholder={baseExternalPerspective}
                    formVal={externalPerspective}
                    formFunction={setExternalPerspective}
                    toolTipCopy={TipList[2].explanation}
                    hasToolTip={true}
                    isComplete={externalPerspective.length != 0}
                />
            </div>
        </div>
    );
}

export default NarrationEditor;
