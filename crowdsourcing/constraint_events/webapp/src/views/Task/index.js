import React, { useEffect } from "react";

import "./styles.css"

import Header from "../../components/Header";
import Constraints from "./Constraints"
import Events from "./Events"

const Task = ({  }) => {
    return (
      <div>
        <Header/>
        <div className="task-container">
            <Events/>
            <Constraints/>
        </div>
      </div>
    );
}

export default Task ;
