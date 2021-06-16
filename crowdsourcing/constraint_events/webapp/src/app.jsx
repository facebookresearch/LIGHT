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
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  //Events State
  const [timesRemaining, setTimesRemaining] = useState("");
  const [broadcastMessage, setBroadcastMessage] = useState("");
  const [isCreatingEntity, setIsCreatingEntity] = useState(false);
  const [createdEntity, setcreatedEntity] = useState(null);
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
        <section className="hero is-medium is-link">
          <div className="hero-body">
            <TaskDescription />
          </div>
        </section>
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
    'times_remaining': timesRemaining
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
    //ERROR HANDLING
    if(!updatedBroadcastMessage){

    }
  // EVENT UPDATES
    let updatedBroadcastMessage = broadcastMessage;
    let updatedEvents = [
      {
        type: "broadcast_message",
        params: {
          self_view: dummyData.interaction,
          room_view: updatedBroadcastMessage
          }
        }
    ]
    let updatedConstraints = [

    ]

    if(isRemovingObjects){
      let updatedRemovedObjects = removedObjects.map(obj=>(
        {type:"remove_object",
          params:{
            name:obj
          }
      }))
      updatedEvents = [...updatedEvents, ...updatedRemovedObjects]
    }
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
    // CONSTRAINT UPDATES
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
      updatedConstraints = [...updatedConstraints, ...updatedPrimaryModifiedAttributes]
    }
    if(updatedSecondaryConstrainingAttributes.length){
      let updatedSecondaryConstrainingAttributes = secondaryConstrainingAttributes.map(attribute=>({
        type:"attribute_compare_value",
        params:{
          type:"in_used_target_item",
          key: attribute.name,
          list: [attribute.value],
          cmp_type: "eq"
        }
      }))
      updatedConstraints = [...updatedConstraints, ...updatedSecondaryModifiedAttributes]
    }
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

    const payload = {
        remaining_uses: remainingUses,
        reversible: updatedIsReversible,
        events: updatedEvents,
        constraints: updatedConstraints
    }
    let complete = false
    if(complete){
        handleSubmit(payload)
    }
  }

  return (
    <div>
      <Task data={dummyData}/>
      <div>
        <Submission />
      </div>
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));


/* <section className="hero is-medium is-link">
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
