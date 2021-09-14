/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import ChatInput from "./ChatInput";
import ActionBar from "./ActionBar";
import DisconnectMessage from "./DisconnectMessage";

//ChatControls - render container that holds both chat input and "action bar" which contains quick chat speech bubbles for each npc in vincinity
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
