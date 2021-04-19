import React from "react";

import "./styles.css";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";

import { Tooltip } from "react-tippy";
import { Picker, emojiIndex } from "emoji-mart";
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

  const defaultEmoji = "❓";
  const { presentAgents } = getLocationState(messages);
  const [showEmojiPicker, setShowEmojiPicker] = React.useState(false);
  const [selectedEmoji, setSelectedEmoji] = React.useState(defaultEmoji);

  const chatInputRef = React.useRef();
  React.useLayoutEffect(() => {
    chatInputRef.current.focus();
  }, []);

  React.useEffect(() => {
    if (persona === null || persona.name === null) return;
    const skipWords = ["a", "the", "an", "of", "with", "holding"];
    const tryPickEmojis = !persona
      ? []
      : persona.name
          .split(" ")
          .filter((token) => !!token)
          .map((token) => token.replace(/\.$/, ""))
          .filter((word) => skipWords.indexOf(word.toLowerCase()) === -1)
          .flatMap((term) =>
            emojiIndex.search(term).map((o) => {
              return o.native;
            })
          );

    const autopickedEmoji =
      tryPickEmojis.length > 0 ? tryPickEmojis[0] : defaultEmoji;
    setSelectedEmoji(autopickedEmoji);
  }, [persona, setSelectedEmoji]);

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
        <ChatMessages messages={messages} agents={agents} persona={persona} />
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
      />
    </div>
  );
};

export default ChatDisplay;
