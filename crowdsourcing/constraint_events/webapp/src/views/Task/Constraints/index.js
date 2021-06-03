import React from "react";

import "./styles.css"

import Questions from "./Questions"

const Constraints = () => {
    return (
        <div className="constraints-container">
            <div className="constraints-header">
                <p>CONSTRAINTS</p>
            </div>
            <Questions />
        </div>
    );
}

export default Constraints ;
