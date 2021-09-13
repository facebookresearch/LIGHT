/* REACT */
import React, {
  useState,
  useEffect,
  useCallback,
  useRef,
  useLayoutEffect,
} from "react";
//STYLES
import "./styles.css";
//TOOLTIP
import "react-tippy/dist/tippy.css";
//Custom Components
import ChatMessages from "./ChatMessages";
import ChatControls from "./ChatControls";
//UTILS
import { setCaretPosition } from "../../../utils";

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
  /*---------------STATE----------------*/
  const [enteredText, setEnteredText] = useState("");
  /*---------------REFS----------------*/
  const chatContainerRef = useRef(null);
  const chatInputRef = useRef();
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
  const setTextTellAgent = useCallback(
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
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom, messages]);

  const { presentAgents } = getLocationState(messages);

  useLayoutEffect(() => {
    const { current } = chatInputRef;
    if (current) {
      current.focus();
    }
  }, []);

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
