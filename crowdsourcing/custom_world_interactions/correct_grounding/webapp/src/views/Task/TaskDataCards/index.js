import React from "react";
//Style
import "./styles.css";
//Custom Components
import DataCard from "./DataCard";
import QuestionCopy from "../../../TaskCopy.js";
import BooleanQuestion from "../../../components/Questions/BooleanQuestion";
import MultipleSelectQuestion from "../../../components/Questions/MultipleSelectQuestion";

//TaskDataCards - renders object1, object 2, and interaction datacards with proper layout
const TaskDataCards = ({
    object1, 
    object1_desc, 
    object2, 
    object2_desc,
    rawAction,
    interaction,
    primaryItem,
    setPrimaryItem,
    interactionValid,
    setInteractionValid,
}) => {
    const QuestionList = QuestionCopy.interaction.questions
    const TipList = QuestionCopy.interaction.tutorialCopy;
    return (
       <div className="taskdatacards-container">
            <div className="items-container">
                <DataCard
                    header={object1}
                    body={object1_desc}
                    color="blue"
                />
                <DataCard
                    header={object2}
                    body={object2_desc}
                    color="orange"
                />
            </div>
            <div className="desc-container">
                <DataCard
                    header={rawAction}
                    body={interaction}
                    color="green"
                />
            </div>
            <div>
                <BooleanQuestion
                    question={QuestionList[0]}
                    trueAnswer={{ name: "Yes" }}
                    falseAnswer={{ name: "No" }}
                    formFunction={(v) => setInteractionValid(v)}
                    toolTipCopy={TipList[0].explanation}
                    hasToolTip={true}
                    defaultOption={interactionValid}
                    isComplete={interactionValid !== null}
                />
            </div>
            <div>
                <MultipleSelectQuestion
                    question={QuestionList[1]}
                    answers={[object1, object2, 'either', 'both']}
                    selectFunction={(v) => setPrimaryItem(v[0])}
                    toolTipCopy={TipList[1].explanation}
                    hasToolTip={true}
                    onlySelectOne={true}
                    isComplete={primaryItem !== null}
                />
            </div>
       </div>
    );
}

export default TaskDataCards ;
