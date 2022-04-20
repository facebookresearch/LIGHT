/* REACT */
import React from "react";
//VIEWS
import PreviewView from "./Views/PreviewView"
import Task from "./Views/Task"
import OnboardingView from "./Views/OnboardingView"
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

  let {
    // For auth token
    mephistoWorkerId,
    agentId,

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

  const getAuthToken = remoteProcedure("get_auth_token");
  const [authToken, setAuthToken] = React.useState(null);

  React.useEffect(() => {
    if (agentId === null || mephistoWorkerId == null) {
      return
    }
    if (authToken === null && !agentId.includes('onboarding')) {
      getAuthToken({worker_id: mephistoWorkerId, agent_id: agentId}).then((res) => {
        setAuthToken(res['auth_token'])
      });
    }
  }, [initialTaskData, mephistoWorkerId, agentId])

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
  if (isLoading || authToken === null || initialTaskData['task_data'] == null) {
    return <LoadingScreen />;
  }

  const preauthTuple = mephistoWorkerId + '/' + agentId + '/' + authToken;
  const fullUrl = initialTaskData['task_data']['url'] + 'preauth/' + preauthTuple + "/#/";

  return (
    <ErrorBoundary handleError={handleFatalError}>
      <MephistoContext.Provider value={mephistoProps}>
        <div className="container-fluid" id="ui-container">
          <Task
            url={fullUrl}
            handleSubmit={handleSubmit}
          />
        </div>
      </MephistoContext.Provider>
    </ErrorBoundary>
  );
}


export default LIGHTAppTaskFrame;
