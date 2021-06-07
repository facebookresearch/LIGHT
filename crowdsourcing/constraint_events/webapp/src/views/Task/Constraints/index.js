import React from "react";

import "./styles.css"

import Questions from "./Questions"

const Constraints = ({object1, object2, interaction}) => {
    return (
        <div className="constraints-container">
            <div className="constraints-header">
                <p>CONSTRAINTS</p>
            </div>
            <Questions object1={object1} object1={object2} interaction={interaction} />
        </div>
    );
}

export default Constraints ;
