//REACT
import React, { useEffect } from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import Header from "../../components/Header";
import ScaleQuestion from "../../components/Questions/ScaleQuestion";

const Task = ({data}) => {
  const {trait, scaleRange, actors} = data
    return (
      <div className="task-container">
        <Header/>
        <ScaleQuestion
          scaleRange={scaleRange}
          selection={actors}
          trait={trait}
          isInputHeader={false}
        />
        <ScaleQuestion
          scaleRange={scaleRange}
          selection={actors}
          trait={trait}
          isInputHeader={true}
        />
      </div>
    );
}

export default Task ;
