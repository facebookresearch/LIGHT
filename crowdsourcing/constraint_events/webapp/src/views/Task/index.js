import React, { useEffect } from "react";

import "./styles.css"
//Custom Components
import Header from "../../components/Header";
import TaskDataCards from "./TaskDataCards"
import Constraints from "./Constraints"
import Events from "./Events"

const Task = ({
  data,
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
}) => {
  const {object1, object2, interaction}= data;
    return (
      <div className="view-container">
        <Header/>
        <TaskDataCards
          object1={object1}
          object2={object2}
          interaction={interaction}
        />
        <div className="task-container">
            <Events
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
            <Constraints
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
            />
        </div>
      </div>
    );
}

export default Task ;
