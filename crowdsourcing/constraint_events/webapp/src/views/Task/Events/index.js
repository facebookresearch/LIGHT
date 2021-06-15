import React from "react";

import "./styles.css"

import Questions from "./Questions"

const Events = ({object1, object2, interaction}) => {
    return (
        <div className="events-container">
            <div className="events-header">
                <p>EVENTS</p>
            </div>
            <div className="events-body">
                <Questions object1={object1} object2={object2} interaction={interaction} />
            </div>
        </div>
    );
}

export default Events ;