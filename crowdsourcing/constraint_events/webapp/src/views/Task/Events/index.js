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
