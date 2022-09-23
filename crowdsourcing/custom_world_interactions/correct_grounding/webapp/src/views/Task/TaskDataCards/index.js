import React from "react";
//Style
import "./styles.css";
//Custom Components
import DataCard from "./DataCard";
import TaskButton from "../../../components/TaskButton"

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
                    header={"Interaction Description: " + rawAction}
                    body={interaction}
                    color="green"
                />
            </div>
            <div>
                Does this interaction overall make sense? Is the narration of an event where an actor uses these objects together:
                <TaskButton selectFunction={() => setInteractionValid(true)} name={'Yes'} isSelected={interactionValid === true} />
                <TaskButton selectFunction={() => setInteractionValid(false)} name={'No'} isSelected={interactionValid === false} />
            </div>
            <div>
                Which item is the actor more likely holding/using to do this interaction:
                <TaskButton selectFunction={() => setPrimaryItem(object1)} name={object1} isSelected={primaryItem==object1} />
                <TaskButton selectFunction={() => setPrimaryItem(object2)} name={object2} isSelected={primaryItem==object2} />
                <TaskButton selectFunction={() => setPrimaryItem('either')} name={'either'} isSelected={primaryItem=='either'} />
            </div>
       </div>
    );
}

export default TaskDataCards ;
