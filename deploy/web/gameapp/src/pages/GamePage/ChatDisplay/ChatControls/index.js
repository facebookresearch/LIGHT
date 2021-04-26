import React from "react";

import "./styles.css";

//Custom Components
import ChatInput from "./ChatInput";
import ActionBar from "./ActionBar";

const ChatControls = ({
  persona,
  presentAgents,
  setTextTellAgent,
  getAgentName,
  getEntityId,
  dataModelHost,
  chatInputRef,
  onSubmit,
  enteredText,
  setEnteredText,
  scrollToBottom,
  idle,
  resetIdleTimer,
}) => {
  return (
    <div className="controls">
      {idle ? (
        <div className="disconnect-container">
          <h2 className="disconnect-text">
            You have been disconnected due to inactivity.
          </h2>
        </div>
      ) : (
        <>
          <ChatInput
            onSubmit={onSubmit}
            enteredText={enteredText}
            setEnteredText={setEnteredText}
            chatInputRef={chatInputRef}
            scrollToBottom={scrollToBottom}
            resetIdleTimer={resetIdleTimer}
          />
          <ActionBar
            persona={persona}
            presentAgents={presentAgents}
            setTextTellAgent={setTextTellAgent}
            getAgentName={getAgentName}
            getEntityId={getEntityId}
            dataModelHost={dataModelHost}
          />
        </>
      )}
    </div>
  );
};

export default ChatControls;
