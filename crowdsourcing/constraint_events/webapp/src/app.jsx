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

  const [timesRemaining, setTimesRemaining] = useState("");
  const [remainingUses, setRemainingUses]= useState("")
  const [isReversible, setIsReversible]= useState(false)
  const [broadcastMessage, setBroadcastMessage] = useState("");
  const [isCreatingEntity, setIsCreatingEntity] = useState(false)
  const [createdEntity, setcreatedEntity] = useState("");
  const [modifiedAttributess, setModifiedAttributes]= useState([])

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
      name: "key",
      desc:"A ordinary key that will unlock or lock something.",
      attributes:[
        {name: "hot", val: false},
        {name: "valuable", val: true},
        {name: "brittle", val: false}
      ]
    },
    object2: {
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
      const payload = {
        remaining_uses: "inf",
        reversible: true,
        events: [
          {
              type: ...,
              params: {...},
          },
          ...
        ],
        constraints: [
          {
              type: ...,
              params: {...},
          },
          ...
        ],
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
