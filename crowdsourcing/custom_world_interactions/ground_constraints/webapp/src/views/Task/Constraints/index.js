
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
    createdEntity,
    isCreatingEntity,
    primaryConstrainingAttributes,
    setPrimaryConstrainingAttributes,
    secondaryConstrainingAttributes,
    setSecondaryConstrainingAttributes,
    hasBackstory,
    setHasBackstory,
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
                    isCreatingEntity={isCreatingEntity}
                    createdEntity={createdEntity}
                    primaryConstrainingAttributes={primaryConstrainingAttributes}
                    setPrimaryConstrainingAttributes={setPrimaryConstrainingAttributes}
                    secondaryConstrainingAttributes={secondaryConstrainingAttributes}
                    setSecondaryConstrainingAttributes={setSecondaryConstrainingAttributes}
                    hasBackstory={hasBackstory}
                    setHasBackstory={setHasBackstory}
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
