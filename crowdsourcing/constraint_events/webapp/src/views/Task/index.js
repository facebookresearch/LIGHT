import React, { useEffect } from "react";

import "./styles.css"

import Header from "../../components/Header";
import Constraints from "./Constraints"
import Events from "./Events"

const Task = ({data}) => {
  const {object1, object2, interaction}= data;
    return (
      <div className="view-container">
        <Header/>
        <div className="task-container">
            <Events object1={object1} object1={object2} interaction={interaction}/>
            <Constraints object1={object1} object1={object2} interaction={interaction}/>
        </div>
      </div>
    );
}

export default Task ;
