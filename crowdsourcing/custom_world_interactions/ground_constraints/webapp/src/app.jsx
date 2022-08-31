/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
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
  /*-----------Constraint State-----------*/
  const [isSecondaryHeld, setIsSecondaryHeld] = useState(null);
  const [isReversible, setIsReversible] = useState(null);
  const [isInfinite, setIsInfinite] = useState(null)
  const [timesRemaining, setTimesRemaining] = useState(0);
  const [isLocationConstrained, setIsLocationConstrained] = useState(null);
  const [constraintLocation, setConstraintLocation] = useState("");

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
  const mephistoData = initialTaskData;
  const active = true;
  const broadcastMessage = mephistoData.this_task_state.broadcastMessage;
  const noBackstoryNarration = mephistoData.this_task_state.noBackstoryNarration;
  const isRemovingObjects = mephistoData.this_task_state.isRemovingObjects;
  const removedObjects = mephistoData.this_task_state.removedObjects;
  const isCreatingEntity = mephistoData.this_task_state.isCreatingEntity;
  const createdEntity = mephistoData.this_task_state.createdEntity;
  const isChangingDescription = mephistoData.this_task_state.isChangingDescription;
  const primaryDescription = mephistoData.this_task_state.primaryDescription;
  const secondaryDescription = mephistoData.this_task_state.secondaryDescription;
  const primaryIsChangingLocation = mephistoData.this_task_state.primaryIsChangingLocation;
  const primaryNewLocation = mephistoData.this_task_state.primaryNewLocation;
  const secondaryIsChangingLocation = mephistoData.this_task_state.secondaryIsChangingLocation;
  const secondaryNewLocation = mephistoData.this_task_state.secondaryNewLocation;
  const primaryModifiedAttributes = mephistoData.this_task_state.primaryModifiedAttributes;
  const secondaryModifiedAttributes = mephistoData.this_task_state.secondaryModifiedAttributes;
  const createdModifiedAttributes = mephistoData.this_task_state.createdModifiedAttributes;
  const primaryConstrainingAttributes = mephistoData.this_task_state.primaryConstrainingAttributes;
  const secondaryConstrainingAttributes = mephistoData.this_task_state.secondaryConstrainingAttributes;
  const hasBackstory = mephistoData.this_task_state.hasBackstory;
  console.group("MEPHISTO TASK DATA");
  console.log(mephistoData.this_task_state);
  console.groupEnd();
  const state = {
    'constraints': [],
    'events': [],
    'times_remaining': ""
  }

  for (let i = 0; i < state['constraints'].length; i++) {
    constraint = state['constraints'][i];

    if (constraint['active'] == "" || (constraint['active'] == 1 && constraint['format'] == None)) {
      active = false;
      break;
    } else {
      console.log('This constraint is fine: ', constraint);
    }
  }

  for (let i = 0; i < state['events'].length; i++) {
    useEvent = state['events'][i];

    if (useEvent['active'] == "" || (useEvent['active'] == 1 && useEvent['format'] == None)) {
      active = false;
      break;
    } else {
      console.log('This constraint is fine: ', constraint);
    }
  }

  const submissionHandler = () => {
    let updatedEvents = []
    let updatedConstraints = []
    let updatedErrors = []
    //ERROR HANDLING
    //EVENT ERRORS
    //BROADCAST MESSAGE
    //CONSTRAINT ERRORS
    // EVENT UPDATES
    //BROADCASTMESSAGE
    let updatedBroadcastMessage = broadcastMessage;
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
    //ATTRIBUTE MODIFICATION EVENTS
    if (primaryModifiedAttributes.length) {
      let updatedPrimaryModifiedAttributes = primaryModifiedAttributes.map(attribute => {
        if (!attribute.name) {
          return
        }
        return ({
          type: "modify_attribute_primary",
          params: {
            type: "in_used_item",
            key: attribute.name,
            value: attribute.value
          }
        })
      })
      updatedEvents = [...updatedEvents, ...updatedPrimaryModifiedAttributes]
    }
    if (secondaryModifiedAttributes.length) {
      let updatedSecondaryModifiedAttributes = secondaryModifiedAttributes.map(attribute => {
        if (!attribute.name) {
          return
        }
        return ({
          type: "modify_attribute_secondary",
          params: {
            type: "in_used_target_item",
            key: attribute.name,
            value: attribute.value
          }
        })
      })
      updatedEvents = [...updatedEvents, ...updatedSecondaryModifiedAttributes]
    }
    if (createdModifiedAttributes.length) {
      let updatedCreatedModifiedAttributes = createdModifiedAttributes.map(attribute => {
        if (!attribute.name) {
          return
        }
        return ({
          type: "modify_attribute_created",
          params: {
            type: "in_used_target_item",
            key: attribute.name,
            value: attribute.value
          }
        })
      })
      updatedEvents = [...updatedEvents, ...updatedCreatedModifiedAttributes]
    }
    //CONSTRAINT UPDATES
    //CONSTRAINING ATTRIBUTES

    if (primaryConstrainingAttributes.length) {
      let updatedPrimaryConstrainingAttributes = primaryConstrainingAttributes.map(attribute => {
        if (!attribute.name) {
          return
        }
        return ({
          type: "attribute_compare_value_primary",
          params: {
            type: "in_used_item",
            key: attribute.name,
            list: [attribute.value],
            cmp_type: attribute.value ? "eq" : "neq",
          }
        })
      })
      updatedConstraints = [...updatedConstraints, ...updatedPrimaryConstrainingAttributes]
    }
    if (secondaryConstrainingAttributes.length) {
      let updatedSecondaryConstrainingAttributes = secondaryConstrainingAttributes.map(attribute => {
        if (!attribute.name) {
          return
        }
        return ({
          type: "attribute_compare_value_secondary",
          params: {
            type: "in_used_target_item",
            key: attribute.name,
            list: [attribute.value],
            cmp_type: attribute.value ? "eq" : "neq"
          }
        })
      })
      updatedConstraints = [...updatedConstraints, ...updatedSecondaryConstrainingAttributes]
    }

    updatedConstraints = [...updatedConstraints, {
      type: "has_backstory",
      params: {
        value: hasBackstory,
        key: "has_backstory",
      }
    }]

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
      primaryConstrainingAttributes,
      secondaryConstrainingAttributes,
      primaryModifiedAttributes,
      secondaryModifiedAttributes,
      createdModifiedAttributes,
      hasBackstory,
      isSecondaryHeld,
      isReversible,
      isInfinite,
      timesRemaining,
      isLocationConstrained,
      constraintLocation,
      ...initialTaskData
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
        noBackstoryNarration={noBackstoryNarration}
        setBroadcastMessage={() => {}}
        isCreatingEntity={isCreatingEntity}
        setIsCreatingEntity={() => {}}
        createdEntity={createdEntity}
        setCreatedEntity={() => {}}
        isRemovingObjects={isRemovingObjects}
        setIsRemovingObjects={() => {}}
        removedObjects={removedObjects}
        setRemovedObjects={() => {}}
        isChangingDescription={isChangingDescription}
        setIsChangingDescription={() => {}}
        primaryDescription={primaryDescription}
        setPrimaryDescription={() => {}}
        secondaryDescription={secondaryDescription}
        setSecondaryDescription={() => {}}
        primaryIsChangingLocation={primaryIsChangingLocation}
        setPrimaryIsChangingLocation={() => {}}
        primaryNewLocation={primaryNewLocation}
        setPrimaryNewLocation={() => {}}
        secondaryIsChangingLocation={secondaryIsChangingLocation}
        setSecondaryIsChangingLocation={() => {}}
        secondaryNewLocation={secondaryNewLocation}
        setSecondaryNewLocation={() => {}}
        primaryModifiedAttributes={primaryModifiedAttributes}
        setPrimaryModifiedAttributes={() => {}}
        secondaryModifiedAttributes={secondaryModifiedAttributes}
        setSecondaryModifiedAttributes={() => {}}
        createdModifiedAttributes={createdModifiedAttributes}
        setCreatedModifiedAttributes={() => {}}
        primaryConstrainingAttributes={primaryConstrainingAttributes}
        setPrimaryConstrainingAttributes={() => {}}
        secondaryConstrainingAttributes={secondaryConstrainingAttributes}
        setSecondaryConstrainingAttributes={() => {}}
        hasBackstory={hasBackstory}
        setHasBackstory={() => {}}
        isInfinite={isInfinite}
        setIsInfinite={setIsInfinite}
        timesRemaining={timesRemaining}
        setTimesRemaining={setTimesRemaining}
        isSecondaryHeld={isSecondaryHeld}
        setIsSecondaryHeld={setIsSecondaryHeld}
        isReversible={isReversible}
        setIsReversible={setIsReversible}
        isLocationConstrained={isLocationConstrained}
        setIsLocationConstrained={setIsLocationConstrained}
        constraintLocation={constraintLocation}
        setConstraintLocation={setConstraintLocation}
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
          isSecondaryHeld={isSecondaryHeld}
          isReversible={isReversible}
          isInfinite={isInfinite}
          timesRemaining={timesRemaining}
          isLocationConstrained={isLocationConstrained}
          constraintLocation={constraintLocation}
        />
      </div>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
