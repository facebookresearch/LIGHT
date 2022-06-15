/* REACT */
import React from "react";
//VIEWS
import PreviewView from "./Views/PreviewView"
import Task from "./Views/Task"
import OnboardingView from "./Views/OnboardingView"

import 'bootstrap/dist/css/bootstrap.min.css';
// Task context
import {
  MephistoContext,
  useMephistoRemoteProcedureTask,
  ErrorBoundary,
} from "mephisto-task";


// TODO move somewhere shared
function LoadingScreen({ children }) {
  return (
    <section className="hero is-light">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">Loading...</p>
        </div>
      </div>
    </section>
  );
}


function LIGHTAppTaskFrame() {
  let mephistoProps = useMephistoRemoteProcedureTask({});

  let{
    // For blocked workers
    blockedReason,
    blockedExplanation,

    // For current state
    isPreview,
    isLoading,
    isOnboarding,

    // For IO
    initialTaskData,
    handleSubmit,
    remoteProcedure,
    handleFatalError,
  } = mephistoProps;

  const getRoomAttributes = remoteProcedure("suggest_room")
  const getRoomFill = remoteProcedure("fill_room")
  const suggestRoomContents = remoteProcedure("suggest_room_contents")
  const suggestCharacterContents = remoteProcedure("suggest_character_contents")
  const suggestObjectDescription = remoteProcedure("suggest_object_description")
  const suggestCharacterDescription = remoteProcedure("suggest_character_description")
  const suggestCharacterPersona = remoteProcedure("suggest_character_persona")
  const suggestObjectContents = remoteProcedure("suggest_object_contents")
  const getObjectFill = remoteProcedure("fill_object")
  const getCharacterFill = remoteProcedure("fill_character")
  const api = {
    getRoomAttributes,
    getRoomFill,
    suggestRoomContents,
    suggestCharacterContents,
    suggestCharacterDescription,
    suggestCharacterPersona,
    suggestObjectDescription,
    suggestObjectContents,
    getObjectFill,
    getCharacterFill,
  }

  if (isOnboarding) {
    return <OnboardingView
            onBoardingSubmitFunction={handleSubmit}
          />;
  }
  if (blockedReason !== null) {
    return <h1>{blockedExplanation}</h1>;
  }
  if (isPreview) {
    return <PreviewView />;
  }
  if (isLoading || initialTaskData['task_data'] == null) {
    return <LoadingScreen />;
  }

  return (
    <ErrorBoundary handleError={handleFatalError}>
      <MephistoContext.Provider value={mephistoProps}>

        <div className="container-fluid" id="ui-container">
          <Task
            api={api}
            handleSubmit={handleSubmit}
          />
        </div>
      </MephistoContext.Provider>
    </ErrorBoundary>
  );
}


export default LIGHTAppTaskFrame;
