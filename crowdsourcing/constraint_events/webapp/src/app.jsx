/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, {useState} from "react";
import ReactDOM from "react-dom";
import Task from "./views/Task";
import Preview from "./views/Preview"
import Submission from "./components/Submission"
import { TaskDescription } from "./components/task_description.jsx";
// import { ActionDescription } from "./components/action_description.jsx";
// import { ConstraintBlock } from "./components/constraint_element.jsx";
// import { EventsBlock } from "./components/event_elements.jsx";
import LoadingScreen from "./components/LoadingScreen"
import { useMephistoTask } from "mephisto-task";
// import { TimesComponent } from "./components/times_component.jsx";
// import { SubmitButton } from "./components/submit_button.jsx";

import "./styles.css"
import 'react-tippy/dist/tippy.css'
/* ================= Application Components ================= */

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
  const [errorMessages, setErrorMessages] = useState("");
  //Events State
  const [broadcastMessage, setBroadcastMessage] = useState("");
  const [isCreatingEntity, setIsCreatingEntity] = useState(null);
  const [createdEntity, setCreatedEntity] = useState(null);
  const [isRemovingObjects, setIsRemovingObjects] = useState(null);
  const [removedObjects, setRemovedObjects] = useState([]);
  const [isChangingDescription, setIsChangingDescription] = useState(false);
    //Primary
  const [primaryModifiedAttributes, setPrimaryModifiedAttributes]= useState([]);
  const [primaryDescription, setPrimaryDescription] = useState("");
    //Secondary
  const [secondaryModifiedAttributes, setSecondaryModifiedAttributes]= useState([]);
  const [secondaryDescription, setSecondaryDescription] = useState("");

  //Constraint State
  const [isSecondaryHeld, setIsSecondaryHeld] = useState(false);
  const [isReversible, setIsReversible] = useState(false);
  const [isInfinite, setIsInifinite] = useState(true)
  const [timesRemaining, setTimesRemaining] = useState(0);
  const [isLocationConstrained, setIsLocationConstrained] = useState(false);
  const [constraintLocation, setConstraintLocation] = useState("");
    //Primary
  const [primaryConstrainingAttributes, setPrimaryConstrainingAttributes]= useState([]);
    //Secondary
  const [secondaryConstrainingAttributes, setSecondaryConstrainingAttributes]= useState([]);


  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div class="hero-body">
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

  // const state = initialTaskData;
  const mephistoData = initialTaskData;

  const active = true;

  const state = {
    'constraints': [],
    'events': [],
    'times_remaining':""
  }

  for (let i = 0; i < state['constraints'].length; i++) {
    constraint = state['constraints'][i];

    if(constraint['active'] == "" || (constraint['active'] == 1 && constraint['format'] == None)) {
      active = false;
      break;
    } else {
      console.log('This constraint is fine: ', constraint);
    }
  }

  for (let i = 0; i < state['events'].length; i++) {
    useEvent = state['events'][i];

    if(useEvent['active'] == "" || (useEvent['active'] == 1 && useEvent['format'] == None)) {
      active = false;
      break;
    } else {
      console.log('This constraint is fine: ', constraint);
    }
  }

  console.log('active? ', active);
    const dummyData= {
      object1: {
        id:2,
        name: "key",
        desc:"A ordinary key that will unlock or lock something.",
        attributes:[
          {name: "hot", val: false},
          {name: "valuable", val: true},
          {name: "brittle", val: false}
        ]
    },
    object2: {
      id:2,
      name: "lock",
      desc:"A ordinary lock that will be unlocked or locked by a key.",
      attributes:[
        {name: "hot", val: false},
        {name: "valuable", val: true},
        {name: "locked", val: true}
      ],
    },
    interaction: "You place the key in the lock and turn.  After a satifying click the lock becomes unlocked."
  }
  const submissionHandler = ()=>{
    let updatedEvents = []
    let updatedConstraints = []
    let updatedTimesRemaining

    //ERROR HANDLING
    if(!broadcastMessage){
      setErrorMessages()
      setShowError(true)
    }
    if(!showError){
  // EVENT UPDATES
    let updatedBroadcastMessage = broadcastMessage;
    updatedBroadcastMessage = {
        type: "broadcast_message",
        params: {
          self_view: dummyData.interaction,
          room_view: broadcastMessage
          }
    }
    updatedEvents = [...updatedEvents, updatedBroadcastMessage]

    //OBJECT REMOVAL EVENT
    if(isRemovingObjects){
      let updatedRemovedObjects = removedObjects.map(obj=>(
        {type:"remove_object",
          params:{
            name:obj
          }
      }))
      updatedEvents = [...updatedEvents, ...updatedRemovedObjects]
    }
    //ENTITY CREATION EVENT
    if(isCreatingEntity){
      const {name, desc, location } = createdEntity;
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
    if(isChangingDescription){
      let updatedDescriptions = [
        {
          type:"modify_attribute",
          params:{
            type:"in_used_item",
            key:"desc",
            value: primaryDescription
          }
        },
        {
          type:"modify_attribute",
          params:{
            type:"in_used_target_item",
            key:"desc",
            value: secondaryDescription
          }
        }
      ]
      updatedEvents = [...updatedEvents, ...updatedDescriptions]
    }
    //ATTRIBUTE MODIFICATION EVENTS
    if(primaryModifiedAttributes.length){
      let updatedPrimaryModifiedAttributes = primaryModifiedAttributes.map(attribute=>({
        type:"modify_attribute",
        params:{
          type:"in_used_item",
          key: attribute.name,
          value: attribute.value
        }
      }))
      updatedEvents = [...updatedEvents, ...updatedPrimaryModifiedAttributes]
    }
    if(secondaryModifiedAttributes.length){
      let updatedSecondaryModifiedAttributes = secondaryModifiedAttributes.map(attribute=>({
        type:"modify_attribute",
        params:{
          type:"in_used_target_item",
          key: attribute.name,
          value: attribute.value
        }
      }))
      updatedEvents = [...updatedEvents, ...updatedSecondaryModifiedAttributes]
    }
    //CONSTRAINT UPDATES
    //CONSTRAINING ATTRIBUTES
    if(primaryConstrainingAttributes.length){
      let updatedPrimaryConstrainingAttributes = primaryConstrainingAttributes.map(attribute=>({
        type:"attribute_compare_value",
        params:{
          type:"in_used_item",
          key: attribute.name,
          list: [attribute.value],
          cmp_type: "eq"
        }
      }))
      updatedConstraints = [...updatedConstraints, ...updatedPrimaryConstrainingAttributes]
    }
    if(secondaryConstrainingAttributes.length){
      let updatedSecondaryConstrainingAttributes = secondaryConstrainingAttributes.map(attribute=>({
        type:"attribute_compare_value",
        params:{
          type:"in_used_target_item",
          key: attribute.name,
          list: [attribute.value],
          cmp_type: "eq"
        }
      }))
      updatedConstraints = [...updatedConstraints, ...updatedSecondaryConstrainingAttributes]
    }
    // HELD CONSTRAINT
    if(isSecondaryHeld){
      let updatedSecondaryHeldConstraint = {
          type: "is_holding",
          params: {
            complement: "used_target_item"
          }
      }
      updatedConstraints = [...updatedConstraints, updatedSecondaryHeldConstraint]
    }
    let updatedIsReversible = isReversible;

    //TIMES REMAINING CONSTRAINT
    if(isInfinite){
      updatedTimesRemaining = "inf"
    }else{
      updatedTimesRemaining = timesRemaining
    }

    // LOCATION CONSTRAINT
    if(isLocationConstrained){
      let updatedLocationConstraint = {
        type: "in_room",
        params: {
            room_name: constraintLocation
        }
      }
      updatedConstraints = [...updatedConstraints, updatedLocationConstraint]
    }
    const payload = {
        times_remaining: updatedTimesRemaining,
        reversible: updatedIsReversible,
        events: updatedEvents,
        constraints: updatedConstraints
    }
    console.log(payload)
    //handleSubmit(payload)
    }
  }

  return (
    <div>
      <Task
        data={dummyData}
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
        setIsInifinite={setIsInifinite}
        timesRemaining={timesRemaining}
        setTimesRemaining={setTimesRemaining}
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


/*
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  //Events State
  const [timesRemaining, setTimesRemaining] = useState("");
  const [broadcastMessage, setBroadcastMessage] = useState("");
  const [isCreatingEntity, setIsCreatingEntity] = useState(false);
  const [createdEntity, setCreatedEntity] = useState(null);
  const [isRemovingObjects, setIsRemovingObjects] = useState("");
  const [removedObjects, setRemovedObjects] = useState([]);
  const [isChangingDescription, setIsChangingDescription] = useState(false);
    //Primary
  const [primaryRemainingUses, setPrimaryRemainingUses]= useState("");
  const [primaryModifiedAttributes, setPrimaryModifiedAttributes]= useState([]);
  const [primaryDescription, setPrimaryDescription] = useState("");
    //Secondary
  const [secondaryRemainingUses, setSecondaryRemainingUses]= useState("");
  const [secondaryModifiedAttributes, setSecondaryModifiedAttributes]= useState([]);
  const [secondaryDescription, setSecondaryDescription] = useState("");

  //Constraint State
  const [isSecondaryHeld, setIsSecondaryHeld] = useState(false);
  const [isReversible, setIsReversible] = useState(false);
  const [isLocationConstrained, setIsLocationConstrained] = useState(false);
  const [constraintLocation, setConstraintLocation] = useState("");
    //Primary
  const [primaryConstrainingAttributes, setPrimaryConstrainingAttributes]= useState([]);
    //Secondary
  const [secondaryConstrainingAttributes, setSecondaryConstrainingAttributes]= useState([]);

<section className="hero is-medium is-link">
  <div className="hero-body">
    <TaskDescription />
    <br />
    <br />
    <ActionDescription state={mephistoData} />
    <br />
    <ConstraintBlock state={mephistoData} constraintArray={state['constraints']} />
    <br />
    <EventsBlock state={mephistoData} eventArray={state['events']} />
    <br />
    <TimesComponent setTimesRemaining={setTimesRemaining} />
    <br />
    <SubmitButton active={active} state={state} onSubmit={handleSubmit}/>
  </div>
</section> */

//     const updatePrimary = {
  //       object_id: {
  //         "name": "object_name",
  //         "contain_size": 0,
  //       remaining_uses: remainingUses,
  //       reversible: true,
  //       events: [
  //         {
  //             type: ...,
  //             params: {...},
  //         },
  //         {
  //         type: "broadcast_message",
  //         params: {
  //           self_view: dummyData.interaction,
  //           room_view:
  //           }
  //         }


  //       ],
  //       constraints: [
  //         {
  //             type: ...,
  //             params: {...},
  //         },
  //         ...
  //       ],
  //   }
  // }
