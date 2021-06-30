//REACT
import React, {useState, useEffect} from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import TaskButton from "../TaskButton"
import Checklist from "./Checklist"

const Submission = ({
    submitFunction,
    broadcastMessage,
    isCreatingEntity,
    createdEntity,
    isRemovingObjects,
    removedObjects,
    isChangingDescription,
    isSecondaryHeld,
    isReversible,
    isInfinite,
    timesRemaining,
    isLocationConstrained,
    constraintLocation
})=>{

    const dummydata = {
        eventsData:[
            {status:true, question: "1. Narrate this interaction to another observer who sees it happen. "},
            {status:true, question: "2. Are objects removed?"},
            {status:true, question: "3. Are objects transformed?"},
            {status:true, question: "4. Are objects created?"},
        ],
        constraintData:[
            {status:true, question: "1. Does Lock need to be held? "},
            {status:true, question: "2. Could one use Lock with Key and expect the same outcome?"},
            {status:true, question: "3. Would this have to happen in a specific place?"},
        ]
    }
    return(
        <div className="submission-container" >
            <div className="submission-checklists">
                <Checklist
                    header="Event Checklist"
                    headerColor="coral"
                    data={dummydata.eventsData}
                />
                <Checklist
                    header="Constraint Checklist"
                    headerColor="red"
                    data={dummydata.constraintData}

                />
            </div>
            <TaskButton
                name="Submit"
                isSelected={false}
                unselectedContainer="submission-button__container"
                unselectedText="submission-selectedbutton__text "
                selectFunction={submitFunction}
            />
        </div>
    )
}
export default Submission;
