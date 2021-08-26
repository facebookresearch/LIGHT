/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */


import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";


import {LoadingScreen } from "./components/LoadingScreen";
import { useMephistoTask, ErrorBoundary } from "mephisto-task";

/* ================= Container Components ================= */
import Preview from "./Views/Preview";
import Task from "./Views/Task";

/* ================= Application Components ================= */

function MainApp() {


  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
    handleFatalError,
    isOnboarding,
    loaded
  } = useMephistoTask();

  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div class="hero-body">
          <h2 className="title is-3">{blockedExplanation}</h2>{" "}
        </div>
      </section>
    );
  }
  if (isLoading) {
    return <LoadingScreen />;
  }
  if (isPreview) {
    return (
      <Preview/>
    );
  }


  return (
    <>
      <ErrorBoundary handleError={handleFatalError}>
        <Task/>
      </ErrorBoundary>
    </>
  )
}

ReactDOM.render(<MainApp />, document.getElementById("app"));





// import React, { useEffect, useState } from "react";
// import ReactDOM from "react-dom";
// import ViewRouter from "./ViewRouter"

// import { useMephistoTask } from "mephisto-task";

// const MainApp = ()=>{
//   const appData = useMephistoTask();

//   return(
//       <div>
//       {
//         appData ?
//         <ViewRouter appData={appData} />
//         :
//         <div/>
//       }
//     </div>
//   )

// }

// ReactDOM.render(<MainApp />, document.getElementById("app"));
