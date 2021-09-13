/* REACT */
import React, { useState } from "react";
//STYLES
import "./styles.css";
//Custom Components
import ChatInput from "./ChatInput";
import ActionBar from "./ActionBar";
import DisconnectMessage from "./DisconnectMessage";

const ChatControls = ({
  presentAgents,
  getAgentName,
  getEntityId,
  dataModelHost,
  onSubmit,
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
            scrollToBottom={scrollToBottom}
            resetIdleTimer={resetIdleTimer}
          />
          <ActionBar
            presentAgents={presentAgents}
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
