import React from "react";
import "./styles.css";
//CUSTOM COMPONENTS
import CollapsibleContainer from "../../components/CollapsibleContainer";
import TaskDescription from "../../components/TaskDescription";

const Task1 = ()=> {
  return (
    <div className="app-container" >
      <div className="header">
        <h1 className="header__text">Object Interaction Narrations</h1>
      </div>
      <CollapsibleContainer>
        <TaskDescription/>
      </CollapsibleContainer>

    </div>
  );
}

export default Task1 ;
