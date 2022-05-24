//REACT
import React, { useEffect } from "react";
//STYLING
import "./styles.css"
//Custom Components
import Header from "../../components/Header";
import TaskDataCards from "./TaskDataCards"
import Events from "./Events"
//Task - Primary View for task, contains the Header, both the events and constraints, and the Task Cards.
const Task = ({
  data,//Data from backend
  //STATE AND CORRESPONDING FUNCTIONS TO SET STATE
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
}) => {
  //Abstracts object and interaction information off data from backend
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
            />
        </div>
      </div>
    );
}

export default Task ;
