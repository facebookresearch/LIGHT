import React from "react";

import "./styles.css";
import "react-tippy/dist/tippy.css";

import { Tooltip } from "react-tippy";
import cx from "classnames";
import onClickOutside from "react-onclickoutside";

//Custom Components
import Entry from "./ChatMessages/Entry";
import ChatMessages from "./ChatMessages";
import ChatControls from "./ChatControls";

import { setCaretPosition } from "../../../utils";

import CONFIG from "../../../config.js";

//Icons
import { FaStar } from "react-icons/fa";
import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";

const ChatDisplay = ({
  messages,
  onSubmit,
  persona,
  location,
  agents,
  getDataModelAddress,
  getLocationState,
  idle,
  resetIdleTimer,
  setPlayerXp,
  setPlayerGiftXp,
  playerGiftXp,
  playerXp,
  sessionGiftXpSpent,
  setSessionGiftXpSpent,
}) => {
  const [showCharacter, setShowCharacter] = React.useState(true);
  const [enteredText, setEnteredText] = React.useState("");
  const chatContainerRef = React.useRef(null);
  const getAgentName = (agent) => (agents ? agents[agent] : agent);
  const getEntityId = (agent) => agent.match(/\d+$/)[0];
  const dataModelHost = getDataModelAddress();

  const scrollToBottom = React.useCallback(
    () =>
      setTimeout(() => {
        if (chatContainerRef.current)
          chatContainerRef.current.scrollTop =
            chatContainerRef.current.scrollHeight;
      }, 0),
    [chatContainerRef]
  );

  React.useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom, messages]);

  const { presentAgents } = getLocationState(messages);

  const chatInputRef = React.useRef();
  React.useLayoutEffect(() => {
    chatInputRef.current.focus();
  }, []);

  const setTextTellAgent = React.useCallback(
    (agent) => {
      const message = `tell ${agent} ""`;
      setEnteredText(message);
      setTimeout(
        () => setCaretPosition(chatInputRef.current, message.length - 1),
        0 /* 0s timeout to schedule this task to occur after the layout is updated */
      );
    },
    [setEnteredText, chatInputRef]
  );

  return (
    <div className="chat-wrapper">
      <div className="chat" ref={chatContainerRef}>
        <ChatMessages
          messages={messages}
          agents={agents}
          persona={persona}
          setTextTellAgent={setTextTellAgent}
          setPlayerXp={setPlayerXp}
          setPlayerGiftXp={setPlayerGiftXp}
          playerGiftXp={playerGiftXp}
          playerXp={playerXp}
          sessionGiftXpSpent={sessionGiftXpSpent}
          setSessionGiftXpSpent={setSessionGiftXpSpent}
        />
      </div>
      <ChatControls
        onSubmit={onSubmit}
        persona={persona}
        presentAgents={presentAgents}
        setTextTellAgent={setTextTellAgent}
        getAgentName={getAgentName}
        getEntityId={getEntityId}
        dataModelHost={dataModelHost}
        chatInputRef={chatInputRef}
        setEnteredText={setEnteredText}
        enteredText={enteredText}
        scrollToBottom={scrollToBottom}
        idle={idle}
        resetIdleTimer={resetIdleTimer}
      />
    </div>
  );
};

export default ChatDisplay;
