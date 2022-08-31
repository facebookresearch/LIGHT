/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";
import { TaskDescription } from "./components/task_description.jsx";
// import { ActionDescription } from "./components/action_description.jsx";
// import { ConstraintBlock } from "./components/constraint_element.jsx";
// import { EventsBlock } from "./components/event_elements.jsx";
//MEPHISTO
import { useMephistoTask } from "mephisto-task";
// import { TimesComponent } from "./components/times_component.jsx";
// import { SubmitButton } from "./components/submit_button.jsx";
//STYLING
import "./styles.css";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-tippy/dist/tippy.css'
//CUSTOM COMPONENTS
import Task from "./views/Task";
import Preview from "./views/Preview";
import Submission from "./components/Submission";
import LoadingScreen from "./components/LoadingScreen";
import ErrorToast from "./components/ErrorToast";
//UTILS
import TaskCopy from "./TaskCopy";

function MainApp() {
  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
  } = useMephistoTask();

  //Error Handling
  const [showError, setShowError] = useState(false);
  const [errorMessages, setErrorMessages] = useState([]);
  /*-----------Events State-----------*/
  const [broadcastMessage, setBroadcastMessage] = useState("");
  const [ranges, setRanges] = useState([]);
  const [isCreatingEntity, setIsCreatingEntity] = useState(null);
  const [createdEntity, setCreatedEntity] = useState({});
  // const [isRemovingObjects, setIsRemovingObjects] = useState(null);
  // default removing objects to true to encourage removing when applicable
  const [isRemovingObjects, setIsRemovingObjects] = useState(true);
  const [removedObjects, setRemovedObjects] = useState([]);
  // const [isChangingDescription, setIsChangingDescription] = useState(null);
  // default changing description to true to encourage writing new description text
  const [isChangingDescription, setIsChangingDescription] = useState(true);
  //Primary
  const [primaryIsChangingLocation, setPrimaryIsChangingLocation] = useState(false);
  const [primaryNewLocation, setPrimaryNewLocation] = useState(null);
  const [primaryDescription, setPrimaryDescription] = useState("");
  //Secondary
  const [secondaryIsChangingLocation, setSecondaryIsChangingLocation] = useState(false);
  const [secondaryNewLocation, setSecondaryNewLocation] = useState(null);
  const [secondaryDescription, setSecondaryDescription] = useState("");


  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div className="hero-body">
          <h2 className="title is-3">{blockedExplanation}</h2>{" "}
        </div>
      </section>
    );
  }

  if (isPreview) {
    return (
      <div>
        <Preview />
      </div>
    );
  }

  // Check if initial task data returns null
  if (isLoading || initialTaskData == null) {
    return <LoadingScreen />;
  }

  const active = true;

  const state = {
    'constraints': [],
    'events': [],
    'times_remaining': ""
  }

  console.log('active? ', active);
  const mephistoData = initialTaskData;

  const submissionHandler = () => {
    let updatedEvents = []
    let updatedConstraints = []
    let updatedErrors = []
    //ERROR HANDLING
    //EVENT ERRORS
    //BROADCAST MESSAGE
    if (!broadcastMessage) {
      updatedErrors.push(TaskCopy.errorKey.events.q1Blank)
    }
    if (broadcastMessage === mephistoData.interaction) {
      updatedErrors.push(TaskCopy.errorKey.events.q1Blank)
    }
    //REMOVE OBJECT
    if (isRemovingObjects === null) {
      updatedErrors.push(TaskCopy.errorKey.events.q2Null)
    }
    if (isRemovingObjects && !removedObjects.length) {
      updatedErrors.push(TaskCopy.errorKey.events.q2Empty)
    }
    // DESCRIPTION
    if (isChangingDescription === null) {
      updatedErrors.push(TaskCopy.errorKey.events.q3Null)
    }
    if (isChangingDescription && (!primaryDescription || !secondaryDescription)) {
      updatedErrors.push(TaskCopy.errorKey.events.q3Blank);
    }
    if (isChangingDescription && (primaryDescription === mephistoData.object1.desc && secondaryDescription === mephistoData.object2.desc)) {
      updatedErrors.push(TaskCopy.errorKey.events.q3NoChange);
    }
    //CREATE ENTITY
    if (isCreatingEntity === null) {
      updatedErrors.push(TaskCopy.errorKey.events.q4Null)
    }
    //LOCATION CHANGE
    if ((primaryIsChangingLocation && !primaryNewLocation) || (secondaryIsChangingLocation && !secondaryNewLocation)) {
      updatedErrors.push(TaskCopy.errorKey.events.q5Blank)
    }
    // EVENT UPDATES
    //BROADCASTMESSAGE
    let updatedBroadcastMessage = broadcastMessage;
    let this_task_state = {
      broadcastMessage,
      isRemovingObjects,
      removedObjects,
      isCreatingEntity,
      createdEntity,
      isChangingDescription,
      primaryDescription,
      secondaryDescription,
      primaryIsChangingLocation,
      primaryNewLocation,
      secondaryIsChangingLocation,
      secondaryNewLocation,
      ranges,
      ...initialTaskData
    }
    updatedBroadcastMessage = {
      type: "broadcast_message",
      params: {
        self_view: mephistoData.interaction,
        room_view: broadcastMessage
      }
    }
    updatedEvents = [...updatedEvents, updatedBroadcastMessage]

    //OBJECT REMOVAL EVENT
    if (isRemovingObjects) {
      let updatedRemovedObjects = removedObjects.map(obj => (
        {
          type: "remove_object",
          params: {
            name: obj
          }
        }))
      updatedEvents = [...updatedEvents, ...updatedRemovedObjects]
    }
    //ENTITY CREATION EVENT
    if (isCreatingEntity) {
      const { name, desc, location } = createdEntity;
      let updatedCreatedEntityEvent = {
        type: "create_entity",
        params: {
          "type": location,
          object: {
            name: name,
            desc: desc
          }
        }
      }
      updatedEvents = [...updatedEvents, updatedCreatedEntityEvent]
    }
    //DESCRIPTION CHANGE EVENT
    if (isChangingDescription) {
      let updatedDescriptions = [
        {
          type: "modify_attribute_primary_description",
          params: {
            type: "in_used_item",
            key: "desc",
            value: primaryDescription
          }
        },
        {
          type: "modify_attribute_secondary_description",
          params: {
            type: "in_used_target_item",
            key: "desc",
            value: secondaryDescription
          }
        }
      ]
      updatedEvents = [...updatedEvents, ...updatedDescriptions]
    }
    // LOCATION CHANGE EVENT
    //Primary
    if (primaryIsChangingLocation && primaryNewLocation) {
      let updatedlLocation = [
        {
          type: "modify_attribute_primary_location",
          params: {
            type: "in_used_item",
            key: "location",
            value: primaryNewLocation
          }
        }
      ]
      updatedEvents = [...updatedEvents, ...updatedlLocation]
    }
    //Secondary
    if (secondaryIsChangingLocation && secondaryNewLocation) {
      let updatedlLocation = [
        {
          type: "modify_attribute_secondary_location",
          params: {
            type: "in_used_target_item",
            key: "location",
            value: secondaryNewLocation
          }
        }
      ]
      updatedEvents = [...updatedEvents, ...updatedlLocation]
    }
    // Actualy data payload properly formatted for submission
    const payload = {
      events: updatedEvents,
      constraints: updatedConstraints,
      this_task_state
    }
    // If the function has reached this point with an empty error array the payload is ready.
    if (!updatedErrors.length) {
      console.log(payload)
      handleSubmit(payload)
    } else {
      // Each error in the updatedErrors Array will be listed in the Error Toast
      setErrorMessages(updatedErrors)
      setShowError(true)
    }
  }
  return (
    <div>
      <ErrorToast errors={errorMessages} showError={showError} hideError={() => setShowError(false)} />
      <Task
        data={mephistoData}
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
      <div>
        <Submission
          submitFunction={submissionHandler}
          broadcastMessage={broadcastMessage}
          isCreatingEntity={isCreatingEntity}
          createdEntity={createdEntity}
          isRemovingObjects={isRemovingObjects}
          removedObjects={removedObjects}
          isChangingDescription={isChangingDescription}
        />
      </div>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
