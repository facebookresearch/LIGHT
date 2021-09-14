/* REACT */
import React, { useEffect, useCallback, useRef } from "react";
/* STYLES */
import "./styles.css";
/* TOOLTIPS */
import "react-tippy/dist/tippy.css";
/* CUSTOM COMPONENTS */
import ChatMessages from "./ChatMessages";
import ChatControls from "./ChatControls";
/* UTILS */
import { setCaretPosition } from "../../../utils";

//ChatDisplay - renders primary container for both chat and entirety of chat controls
const ChatDisplay = ({
  messages,
  onSubmit,
  agents,
  getDataModelAddress,
  getLocationState,
  idle,
  resetIdleTimer,
}) => {
  /*---------------REFS----------------*/
  const chatContainerRef = useRef(null);
  /*---------------UT----------------*/
  const getAgentName = (agent) => (agents ? agents[agent] : agent);
  const getEntityId = (agent) => agent.match(/\d+$/)[0];
  const dataModelHost = getDataModelAddress();
  /*---------------CALLBACKS----------------*/
  const scrollToBottom = useCallback(
    () =>
      setTimeout(() => {
        if (chatContainerRef.current)
          chatContainerRef.current.scrollTop =
            chatContainerRef.current.scrollHeight;
      }, 0),
    [chatContainerRef]
  );
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom, messages]);

  const { presentAgents } = getLocationState(messages);

  // useLayoutEffect(() => {
  //   const { current } = chatInputRef;
  //   if (current) {
  //     current.focus();
  //   }
  // }, []);

  return (
    <div className="chat-wrapper">
      <div className="chat" ref={chatContainerRef}>
        <ChatMessages messages={messages} />
      </div>
      <ChatControls
        onSubmit={onSubmit}
        presentAgents={presentAgents}
        getAgentName={getAgentName}
        getEntityId={getEntityId}
        dataModelHost={dataModelHost}
        scrollToBottom={scrollToBottom}
        idle={idle}
        resetIdleTimer={resetIdleTimer}
      />
    </div>
  );
};

export default ChatDisplay;
