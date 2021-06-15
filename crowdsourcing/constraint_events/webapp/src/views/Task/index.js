import React, { useEffect } from "react";

import "./styles.css"
//Custom Components
import Header from "../../components/Header";
import TaskDataCards from "./TaskDataCards"
import Constraints from "./Constraints"
import Events from "./Events"

const Task = ({data}) => {
  const {object1, object2, interaction}= data;
    return (
      <div className="view-container">
        <Header/>
        <TaskDataCards
          object1={object1}
          object2={object2}
          interaction={interaction}
        />
        <div className="task-container">
            <Events object1={object1} object2={object2} interaction={interaction}/>
            <Constraints object1={object1} object2={object2} interaction={interaction}/>
        </div>
      </div>
    );
}

export default Task ;
