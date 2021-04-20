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
}) => {
  return (
    <div className="controls">
      <ChatInput
        onSubmit={onSubmit}
        enteredText={enteredText}
        setEnteredText={setEnteredText}
        chatInputRef={chatInputRef}
        scrollToBottom={scrollToBottom}
      />
      <ActionBar
        persona={persona}
        presentAgents={presentAgents}
        setTextTellAgent={setTextTellAgent}
        getAgentName={getAgentName}
        getEntityId={getEntityId}
        dataModelHost={dataModelHost}
      />
    </div>
  );
};

export default ChatControls;
