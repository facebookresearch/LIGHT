import React from "react";
import "./styles.css";
//CUSTOM COMPONENTS
import TaskDescription from "../../components/TaskDescription";

const Preview = ()=> {
  return (
    <div className="app-container" >
        <div className="header">
          <h1 className="header__text">Object Interaction Narrations</h1>
        </div>
      <TaskDescription/>
    </div>
  );
}

export default Preview ;
