//REACT
import React, { useEffect } from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import Header from "../../components/Header";
import ScaleQuestion from "../../components/Questions/ScaleQuestion";

const Task = ({data}) => {
    return (
      <div className="view-container">
        <Header/>
        <ScaleQuestion/>
      </div>
    );
}

export default Task ;
