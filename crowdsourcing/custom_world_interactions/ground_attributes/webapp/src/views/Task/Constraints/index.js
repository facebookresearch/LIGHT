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
    createdEntity,
    isCreatingEntity,
    primaryConstrainingAttributes,
    setPrimaryConstrainingAttributes,
    secondaryConstrainingAttributes,
    setSecondaryConstrainingAttributes,
    hasBackstory,
    setHasBackstory
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
                    isCreatingEntity={isCreatingEntity}
                    createdEntity={createdEntity}
                    primaryConstrainingAttributes={primaryConstrainingAttributes}
                    setPrimaryConstrainingAttributes={setPrimaryConstrainingAttributes}
                    secondaryConstrainingAttributes={secondaryConstrainingAttributes}
                    setSecondaryConstrainingAttributes={setSecondaryConstrainingAttributes}
                    hasBackstory={hasBackstory}
                    setHasBackstory={setHasBackstory}
                />
            </div>
        </div>
    );
}

export default Constraints ;
