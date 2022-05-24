//REACT
import React, { useEffect } from "react";
//STYLING
import "./styles.css"
//Custom Components
import Header from "../../components/Header";
import TaskDataCards from "./TaskDataCards"
import Constraints from "./Constraints"
import Events from "./Events"
//Task - Primary View for task, contains the Header, both the events and constraints, and the Task Cards.
const Task = ({
  data,//Data from backend
  //STATE AND CORRESPONDING FUNCTIONS TO SET STATE
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
  createdModifiedAttributes,
  setCreatedModifiedAttributes,
  primaryConstrainingAttributes,
  setPrimaryConstrainingAttributes,
  secondaryConstrainingAttributes,
  setSecondaryConstrainingAttributes,
  noBackstoryNarration,
  setNoBackstoryNarration,
  hasBackstory,
  setHasBackstory
}) => {
  //Abstracts object and interaction information off data from backend
  const { object1, object2, interaction } = data;
  return (
    <div className="view-container">
      <Header />
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
          primaryIsChangingLocation={primaryIsChangingLocation}
          setPrimaryIsChangingLocation={setPrimaryIsChangingLocation}
          primaryNewLocation={primaryNewLocation}
          setPrimaryNewLocation={setPrimaryNewLocation}
          secondaryIsChangingLocation={secondaryIsChangingLocation}
          setSecondaryIsChangingLocation={setSecondaryIsChangingLocation}
          secondaryNewLocation={secondaryNewLocation}
          setSecondaryNewLocation={setSecondaryNewLocation}
          noBackstoryNarration={noBackstoryNarration}
          setNoBackstoryNarration={setNoBackstoryNarration}
          primaryModifiedAttributes={primaryModifiedAttributes}
          setPrimaryModifiedAttributes={setPrimaryModifiedAttributes}
          secondaryModifiedAttributes={secondaryModifiedAttributes}
          setSecondaryModifiedAttributes={setSecondaryModifiedAttributes}
          createdModifiedAttributes={createdModifiedAttributes}
          setCreatedModifiedAttributes={setCreatedModifiedAttributes}
        />
        <Constraints
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

export default Task;
