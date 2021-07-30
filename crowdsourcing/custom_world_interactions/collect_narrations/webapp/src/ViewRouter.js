/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";
import { ObjectSelector } from "./components/object_selector.jsx";
import { InteractionDescription } from "./components/interaction_description.jsx";
import { TaskDescription } from "./components/task_description.jsx";
import { LoadingScreen } from "./components/core_components.jsx";
import { useMephistoTask } from "mephisto-task";
import { SubmitButton } from "./components/submit_button.jsx";

/* ================= Container Components ================= */
import Preview from "./Views/Preview";
import Task1 from "./Views/Task1";

/* ================= Application Components ================= */

const ViewRouter =({appData})=> {

    const [mephistoData, setMephistoData] = useState(null);
    const [primaryObjects, setPrimaryObjects] = React.useState([]);
    const [secondaryObjects, setSecondaryObjects] = React.useState([]);
    const [primaryObject, onChangePrimaryObject] = React.useState("");
    const [secondaryObject, onChangeSecondaryObject] = React.useState("");
    const [actionDescription, onChangeActionDescription] = React.useState("");
    const [otherActive, onChangeOtherActive] = React.useState(false);

  console.log("APP DATA:  ", appData)

  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
    loaded
  } = appData;

  useEffect(()=>{
    if(loaded){
        setMephistoData(initialTaskData)
    }
  }, [loaded])

  useEffect(()=>{
    if( mephistoData && loaded){
        if(mephistoData["primary_object_list"] && mephistoData["secondary_object_list"]){
            setPrimaryObjects(mephistoData["primary_object_list"]);
            setSecondaryObjects(mephistoData["secondary_object_list"]);
        }
    }
  }, [mephistoData])

  const state = {
    primaryObject: primaryObject,
    secondaryObject: secondaryObject,
    actionDescription: actionDescription,
  };

  const active =
    state.actionDescription.length > 0 &&
    state.secondaryObject.length > 0 &&
    state.primaryObject.length > 0;
// if (blockedReason !== null) {
//     return (
//       <section className="hero is-medium is-danger">
//         <div class="hero-body">
//           <h2 className="title is-3">{blockedExplanation}</h2>{" "}
//         </div>
//       </section>
//     );
//   }

//   if (isPreview) {
    return (
    <>
        {
            (blockedReason !== null) ?
            <section className="hero is-medium is-danger">
                <div class="hero-body">
                    <h2 className="title is-3">{blockedExplanation}</h2>{" "}
                </div>
            </section>
            :
            isPreview ?
                <Preview/>:
                (primaryObjects.length && secondaryObjects.length) ?
                    <Task1
                        primaryObjects={primaryObjects}
                        secondaryObjects={secondaryObjects}
                        onChangeCurrentPrimaryObject={onChangePrimaryObject}
                        onChangeCurrentSecondaryObject={onChangeSecondaryObject}
                        otherActive={otherActive}
                        onChangeOtherActive={onChangeOtherActive}
                    />
                    :
                    isLoading ?
                        <LoadingScreen /> :
                        <div/>
        }
    </>
    );
  }

  // Check if initial task data returns null
//   if (isLoading || mephistoData == null) {
//     return <LoadingScreen />;
//   }
//   const primaryObjectList = initialTaskData["primary_object_list"];
//   const secondaryObjectList = initialTaskData["secondary_object_list"];


//   if(primaryObjects && secondaryObjects){
//     return (
//             <Task1
//                 primaryObjects={primaryObjects}
//                 secondaryObjects={secondaryObjects}
//                 onChangeCurrentPrimaryObject={onChangePrimaryObject}
//                 onChangeCurrentSecondaryObject={onChangeSecondaryObject}
//                 otherActive={otherActive}
//                 onChangeOtherActive={onChangeOtherActive}
//             />

// { /*   <div>
//       <section className="hero is-medium is-link">
//         <div className="hero-body">
//           <TaskDescription />
//           <br />
//           <br />
//           <ObjectSelector
//             primaryObjectList={primaryObjectList}
//             secondaryObjectList={secondaryObjectList}
//             onChangeCurrentPrimaryObject={onChangePrimaryObject}
//             onChangeCurrentSecondaryObject={onChangeSecondaryObject}
//             otherActive={otherActive}
//             onChangeOtherActive={onChangeOtherActive}
//           />
//           <br />
//           <br />
//           <p>
//             You are narrating the <b>interaction</b> of a character in a
//             medieval fantasy adventure <b>trying to</b>{" "}
//             <i>
//               "use {state.primaryObject} with {state.secondaryObject}".
//             </i>
//           </p>
//           <InteractionDescription
//             description={state.actionDescription}
//             onChangeDescription={onChangeActionDescription}
//           />
//           <br />
//           <SubmitButton active={active} state={state} onSubmit={handleSubmit} />
//         </div>
//       </section>
//     </div>
// */}
    // )}
// }
export default ViewRouter;
