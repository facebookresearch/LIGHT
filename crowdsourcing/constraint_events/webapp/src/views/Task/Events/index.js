import React from "react";

import "./styles.css"

import Questions from "./Questions"

const Events = () => {
    return (
        <div className="events-container">
            <div className="events-header">
                <p>EVENTS</p>
            </div>
            <Questions />
        </div>
    );
}

export default Events ;
