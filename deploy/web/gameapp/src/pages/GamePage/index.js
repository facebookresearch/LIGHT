import React from "react";

import "../../styles.css";
import "./styles.css";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";

import { Picker, emojiIndex } from "emoji-mart";
import onClickOutside from "react-onclickoutside";

//Custom Components
import { useWSDataSource } from "../../useWSDataSource";
import ExperienceInfo from "../../components/ExperienceInfo";
import Logo from "../../components/Logo/index.js";
import LoadingScreen from "../../LoadingScreen";
import Sidebar from "./Sidebar";
import ChatDisplay from "./ChatDisplay";

import CONFIG from "../../config.js";

const createWebSocketUrlFromBrowserUrl = (url) => {
  const wsProtocol = url.protocol === "https:" ? "wss" : "ws";
  const optionalServerHost = new URL(url).searchParams.get("server");
  var optionalGameId = new URL(url).searchParams.get("id");
  if (!optionalGameId) {
    optionalGameId = "";
  }
  if (optionalServerHost) {
    console.log("Using user-provided server hostname:", optionalServerHost);
  }

  let websocketURL =
    wsProtocol + "://" + (optionalServerHost || CONFIG.hostname);
  if (CONFIG.port != "80") {
    websocketURL += ":" + CONFIG.port;
  }
  websocketURL += `/game${optionalGameId}/socket`;
  return websocketURL;
};

const getDataModelAddress = () => {
  return new URL(window.location).searchParams.get("builder");
};

// TODO: consider showing different agent's dialogues in
// different colors
//
// const colors = [
//   "#edfff1", //green,
//   "#fffded", //yellow,
//   "#eee8ff", // purple
//   "#e6efff", //blue
//   "#ffe8eb" //red
// ];

function ConnectedApp() {
  const wsUrl = React.useMemo(
    () => createWebSocketUrlFromBrowserUrl(window.location),
    []
  );
  const {
    isErrored,
    messages,
    submitMessage,
    persona,
    location,
    agents,
    isFull,
  } = useWSDataSource(wsUrl);

  if (isErrored)
    return (
      <div style={{ textAlign: "center", marginTop: 30, fontSize: 30 }}>
        Could not connect to the server.
      </div>
    );

  if (messages.length === 0) {
    return <LoadingScreen isFull={isFull} />;
  }

  return (
    <Chat
      messages={messages}
      onSubmit={submitMessage}
      persona={persona}
      location={location}
      agents={agents}
    />
  );
}

function Chat({ messages, onSubmit, persona, location, agents }) {
  const [idleTime, setIdleTime] = React.useState(0);
  const [idle, setIdle] = React.useState(false);
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
    let timer = null;
    timer = setInterval(() => {
      setIdleTime((idleTime) => idleTime + 1);
      console.log("TIME", idleTime);
    }, 1000);
    if (idleTime === 300) {
      //disconnect
      setIdle(true);
    }
    return () => clearInterval(timer);
  }, [idleTime]);

  const disconnect = () => {};
  const resetIdleTimer = () => {
    setIdleTime(0);
    console.log("IDLE TIME", idleTime);
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom, messages]);

  const defaultEmoji = "❓";
  const { presentAgents } = getLocationState(messages);
  const [selectedEmoji, setSelectedEmoji] = React.useState(defaultEmoji);

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

  return (
    <div className="App" onMouseMove={resetIdleTimer}>
      {persona ? (
        <Sidebar
          persona={persona}
          location={location}
          dataModelHost={dataModelHost}
          getEntityId={getEntityId}
          selectedEmoji={selectedEmoji}
          setSelectedEmoji={setSelectedEmoji}
        />
      ) : (
        <div />
      )}
      {/* <Map /> */}
      {/* <div className="app-controls">
          <label>
            <input
              type="checkbox"
              checked={isAdminMode}
              onChange={e => setAdminMode(!isAdminMode)}
            />{" "}
            Admin Mode
          </label>
        </div> */}
      <ChatDisplay
        scrollToBottom={scrollToBottom}
        messages={messages}
        onSubmit={onSubmit}
        persona={persona}
        location={location}
        agents={agents}
        getDataModelAddress={getDataModelAddress}
        getLocationState={getLocationState}
        idle={idle}
        resetIdleTimer={resetIdleTimer}
      />
    </div>
  );
}

const EmojiPicker = ({ onBlur, ...props }) => {
  EmojiPicker.handleClickOutside = () => onBlur();
  return <Picker {...props} />;
};
const BlurClosingPicker = onClickOutside(EmojiPicker, {
  handleClickOutside: () => EmojiPicker.handleClickOutside,
});

function getLocationState(messages) {
  var valid_messages = messages.filter(
    (m) => m.is_self !== true && m.caller !== null
  );
  if (valid_messages.length === 0) return [null, []];
  var lastMessage = valid_messages[valid_messages.length - 1];

  return {
    currentRoom: lastMessage.room_id,
    presentAgents: Object.keys(lastMessage.present_agent_ids),
  };
}
export default ConnectedApp;
