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
// Events Component - Container for Events questions
const Events = ({
    object1,
    object2,
    interaction,
    broadcastMessage,
    setBroadcastMessage,
    ranges,
    setRanges,
    isCreatingEntity,
    setIsCreatingEntity,
    createdEntity,
    setCreatedEntity,
    isRemovingObjects,
    setIsRemovingObjects,
    removedObjects,
    setRemovedObjects,
    isChangingDescription,
    setIsChangingDescription,
    primaryDescription,
    setPrimaryDescription,
    secondaryDescription,
    setSecondaryDescription,
    primaryIsChangingLocation,
    setPrimaryIsChangingLocation,
    primaryNewLocation,
    setPrimaryNewLocation,
    secondaryIsChangingLocation,
    setSecondaryIsChangingLocation,
    secondaryNewLocation,
    setSecondaryNewLocation,
    primaryModifiedAttributes,
    setPrimaryModifiedAttributes,
    secondaryModifiedAttributes,
    setSecondaryModifiedAttributes,
}) => {
    return (
        <div className="events-container">
            <div className="events-header">
                <p>EVENTS</p>
            </div>
            <div className="events-body">
                <Questions
                    object1={object1}
                    object2={object2}
                    interaction={interaction}
                    broadcastMessage={broadcastMessage}
                    setBroadcastMessage={setBroadcastMessage}
                    ranges={ranges}
                    setRanges={setRanges}
                    isCreatingEntity={isCreatingEntity}
                    setIsCreatingEntity={setIsCreatingEntity}
                    createdEntity={createdEntity}
                    setCreatedEntity={setCreatedEntity}
                    isRemovingObjects={isRemovingObjects}
                    setIsRemovingObjects={setIsRemovingObjects}
                    removedObjects={removedObjects}
                    setRemovedObjects={setRemovedObjects}
                    isChangingDescription={isChangingDescription}
                    setIsChangingDescription={setIsChangingDescription}
                    primaryDescription={primaryDescription}
                    setPrimaryDescription={setPrimaryDescription}
                    secondaryDescription={secondaryDescription}
                    setSecondaryDescription={setSecondaryDescription}
                    primaryIsChangingLocation={primaryIsChangingLocation}
                    setPrimaryIsChangingLocation={setPrimaryIsChangingLocation}
                    primaryNewLocation={primaryNewLocation}
                    setPrimaryNewLocation={setPrimaryNewLocation}
                    secondaryIsChangingLocation={secondaryIsChangingLocation}
                    setSecondaryIsChangingLocation={setSecondaryIsChangingLocation}
                    secondaryNewLocation={secondaryNewLocation}
                    setSecondaryNewLocation={setSecondaryNewLocation}
                    primaryModifiedAttributes={primaryModifiedAttributes}
                    setPrimaryModifiedAttributes={setPrimaryModifiedAttributes}
                    secondaryModifiedAttributes={secondaryModifiedAttributes}
                    setSecondaryModifiedAttributes={setSecondaryModifiedAttributes}
                />
            </div>
        </div>
    );
}

export default Events ;
