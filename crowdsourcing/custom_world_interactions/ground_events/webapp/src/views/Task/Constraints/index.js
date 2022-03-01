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
    isSecondaryHeld,
    setIsSecondaryHeld,
    isReversible,
    setIsReversible,
    isLocationConstrained,
    setIsLocationConstrained,
    constraintLocation,
    setConstraintLocation,
    primaryConstrainingAttributes,
    setPrimaryConstrainingAttributes,
    secondaryConstrainingAttributes,
    setSecondaryConstrainingAttributes,
    isInfinite,
    setIsInfinite,
    timesRemaining,
    setTimesRemaining,
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
                    isSecondaryHeld={isSecondaryHeld}
                    setIsSecondaryHeld={setIsSecondaryHeld}
                    isReversible={isReversible}
                    setIsReversible={setIsReversible}
                    isLocationConstrained={isLocationConstrained}
                    setIsLocationConstrained={setIsLocationConstrained}
                    constraintLocation={constraintLocation}
                    setConstraintLocation={setConstraintLocation}
                    primaryConstrainingAttributes={primaryConstrainingAttributes}
                    setPrimaryConstrainingAttributes={setPrimaryConstrainingAttributes}
                    secondaryConstrainingAttributes={secondaryConstrainingAttributes}
                    setSecondaryConstrainingAttributes={setSecondaryConstrainingAttributes}
                    isInfinite={isInfinite}
                    setIsInfinite={setIsInfinite}
                    timesRemaining={timesRemaining}
                    setTimesRemaining={setTimesRemaining}
                />
            </div>
        </div>
    );
}

export default Constraints ;
