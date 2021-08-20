import React from "react";

import "./styles.css";

//Custom Components
import ChatInput from "./ChatInput";
import ActionBar from "./ActionBar";
import DisconnectMessage from "./DisconnectMessage";

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
        <DisconnectMessage />
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
