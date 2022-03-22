//REACT
import React from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS
import Questions from "./Questions"

//Constraints -
const Constraints = ({
    object1,
    object2,
    interaction,
    primaryConstrainingAttributes,
    setPrimaryConstrainingAttributes,
    secondaryConstrainingAttributes,
    setSecondaryConstrainingAttributes,
}) => {
    return (
        <div className="constraints-container">
            <div className="constraints-header">
                <p>CONSTRAINTS</p>
            </div>
            <div className="events-body">
                <Questions
                    object1={object1}
                    object2={object2}
                    interaction={interaction}
                    primaryConstrainingAttributes={primaryConstrainingAttributes}
                    setPrimaryConstrainingAttributes={setPrimaryConstrainingAttributes}
                    secondaryConstrainingAttributes={secondaryConstrainingAttributes}
                    setSecondaryConstrainingAttributes={setSecondaryConstrainingAttributes}
                />
            </div>
        </div>
    );
}

export default Constraints ;
