/* REACT */
import React, { useState } from "react";
//STYLES
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
  /*---------------STATE----------------*/
  const [tellTarget, setTellTarget] = useState(null);
  const [isSaying, setIsSaying] = useState(true);
  /*---------------HANDLERS----------------*/
  const isSayingToggleHandler = (e) => {
    setTellTarget(null);
    setIsSaying(!isSaying);
  };
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
            isSaying={isSaying}
            toggleIsSaying={isSayingToggleHandler}
            tellTarget={tellTarget}
          />
          <ActionBar
            persona={persona}
            presentAgents={presentAgents}
            setTextTellAgent={setTextTellAgent}
            getAgentName={getAgentName}
            getEntityId={getEntityId}
            dataModelHost={dataModelHost}
            setIsSaying={setIsSaying}
            setTellTarget={setTellTarget}
          />
        </>
      )}
    </div>
  );
};

export default ChatControls;
