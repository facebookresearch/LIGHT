import React from "react";

import "../../styles.css";
import "./styles.css";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";

import { DefaultEmojiMapper } from "../../utils";

import { Picker, emojiIndex } from "emoji-mart";
import onClickOutside from "react-onclickoutside";

import Scribe from "../../assets/images/scribe.png";
import Beer from "../../assets/images/Beer.png";

//Custom Components
import { useWSDataSource } from "../../useWSDataSource";
import MobileFrame from "../../components/MobileFrame";
import ExperienceInfo from "../../components/ExperienceInfo";
import Logo from "../../components/Logo/index.js";
import LoadingScreen from "../../LoadingScreen";
import Sidebar from "./Sidebar";
import ChatDisplay from "./ChatDisplay";
import Modal from "../../components/Modal";
import InstructionModalContent from "./InstructionModalContent";

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
    disconnectFromSession,
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
      disconnectFromSession={disconnectFromSession}
    />
  );
}

function Chat({
  messages,
  onSubmit,
  persona,
  location,
  agents,
  disconnectFromSession,
}) {
  //MOBILE STATE
  const [screenSize, setScreenSize] = React.useState(null);
  const [isMobile, setIsMobile] = React.useState(false);
  //DRAWER STATE
  const [showDrawer, setShowDrawer] = React.useState(false);
  //MODAL STATE
  const [showInstructionModal, setShowInstructionModal] = React.useState(false);
  //IDLE STATE
  const [idleTime, setIdleTime] = React.useState(0);
  const [idle, setIdle] = React.useState(false);
  //CHAT TEXT STATE
  const [enteredText, setEnteredText] = React.useState("");
  const chatContainerRef = React.useRef(null);
  //PLAYER XP AND GIFT XP
  const [playerXp, setPlayerXp] = React.useState(0);
  const [playerGiftXp, setPlayerGiftXp] = React.useState(0);
  const [sessionXp, setSessionXp] = React.useState(0);
  const [sessionGiftXp, setSessionGiftXp] = React.useState(0);
  const [sessionGiftXpSpent, setSessionGiftXpSpent] = React.useState(0);
  // AGENT AND CHARACTER STATE
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
    }, 1000);
    if (idleTime === 300) {
      setIdle(true);
      clearInterval(timer);
      disconnectFromSession();
    }
    return () => clearInterval(timer);
  }, [idleTime]);

  const resetIdleTimer = () => {
    setIdleTime(0);
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom, messages]);

  // Previous Emoji Mapper
  // const defaultEmoji = "❓";
  // const { presentAgents } = getLocationState(messages);
  // const [selectedEmoji, setSelectedEmoji] = React.useState(defaultEmoji);

  // React.useEffect(() => {
  //   if (persona === null || persona.name === null) return;
  //   const skipWords = ["a", "the", "an", "of", "with", "holding"];
  //   const tryPickEmojis = !persona
  //     ? []
  //     : persona.name
  //         .split(" ")
  //         .filter((token) => !!token)
  //         .map((token) => token.replace(/\.$/, ""))
  //         .filter((word) => skipWords.indexOf(word.toLowerCase()) === -1)
  //         .flatMap((term) =>
  //           emojiIndex.search(term).map((o) => {
  //             return o.native;
  //           })
  //         );

  //   const autopickedEmoji =
  //     tryPickEmojis.length > 0 ? tryPickEmojis[0] : defaultEmoji;
  //   setSelectedEmoji(autopickedEmoji);
  // }, [persona, setSelectedEmoji]);

  const defaultEmoji = "❓";
  const { presentAgents } = getLocationState(messages);
  const [selectedEmoji, setSelectedEmoji] = React.useState(defaultEmoji);

  React.useEffect(() => {
    let characterEmoji = DefaultEmojiMapper(persona.name);
    if (persona === null || persona.name === null) return;
    const skipWords = ["a", "the", "an", "of", "with", "holding"];
    const tryPickEmojis = !persona
      ? []
      : emojiIndex.search(characterEmoji).map((o) => {
          return o.native;
        });
    const autopickedEmoji =
      tryPickEmojis.length > 0 ? tryPickEmojis[0] : defaultEmoji;
    setSelectedEmoji(autopickedEmoji);
  }, [persona, setSelectedEmoji]);

  React.useEffect(() => {
    const { xp, giftXp } = persona;
    if (xp <= 10) {
      setShowInstructionModal(true);
    }
    setPlayerXp(xp);
    setPlayerGiftXp(giftXp);
  }, [persona]);

  React.useEffect(() => {
    let sessionXpUpdate = 0;
    messages.map((message) => {
      if (message.is_self && message.xp > 0) {
        sessionXpUpdate += message.xp;
      }
    });
    setSessionXp(sessionXpUpdate);
  }, [messages]);

  React.useEffect(() => {
    const { xp, giftXp } = persona;
    setPlayerXp(xp + sessionXp);
    let sessionGiftXpUpdate = sessionXp / 4;
    if (sessionGiftXpUpdate >= 1) {
      setPlayerGiftXp(giftXp + sessionGiftXpUpdate - sessionGiftXpSpent);
    } else {
      setPlayerGiftXp(giftXp - sessionGiftXpSpent);
    }
  }, [sessionXp, sessionGiftXpSpent]);

  const updateDimensions = () => {
    setScreenSize(window.innerWidth);
  };
  React.useEffect(() => {
    window.addEventListener("resize", updateDimensions);
    let startingSize = window.innerWidth;
    if (startingSize <= 950) {
      setIsMobile(true);
    } else if (startingSize > 950) {
      setIsMobile(false);
    }
  });

  React.useEffect(() => {
    if (screenSize <= 950) {
      setIsMobile(true);
    } else if (screenSize > 950) {
      setIsMobile(false);
    }
  }, [screenSize]);

  const openDrawer = () => setShowDrawer(true);
  const closeDrawer = () => setShowDrawer(false);
  const buttons = [];
  return (
    <div className="gamepage-container" onMouseMove={resetIdleTimer}>
      {isMobile ? (
        <MobileFrame
          showDrawer={showDrawer}
          openDrawer={openDrawer}
          closeDrawer={closeDrawer}
          buttons={buttons}
        >
          {persona ? (
            <Sidebar
              persona={persona}
              location={location}
              dataModelHost={dataModelHost}
              getEntityId={getEntityId}
              selectedEmoji={selectedEmoji}
              setSelectedEmoji={setSelectedEmoji}
              playerXp={playerXp}
              playerGiftXp={playerGiftXp}
              isMobile={isMobile}
              showDrawer={showDrawer}
            />
          ) : null}
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
            setPlayerXp={setPlayerXp}
            setPlayerGiftXp={setPlayerGiftXp}
            playerXp={playerXp}
            playerGiftXp={playerGiftXp}
            sessionGiftXpSpent={sessionGiftXpSpent}
            setSessionGiftXpSpent={setSessionGiftXpSpent}
          />
        </MobileFrame>
      ) : (
        <>
          <div className="sidebar-container">
            {persona ? (
              <Sidebar
                persona={persona}
                location={location}
                dataModelHost={dataModelHost}
                getEntityId={getEntityId}
                selectedEmoji={selectedEmoji}
                setSelectedEmoji={setSelectedEmoji}
                playerXp={playerXp}
                playerGiftXp={playerGiftXp}
              />
            ) : (
              <div />
            )}
          </div>
          <div className="chat-container">
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
              setPlayerXp={setPlayerXp}
              setPlayerGiftXp={setPlayerGiftXp}
              playerXp={playerXp}
              playerGiftXp={playerGiftXp}
              sessionGiftXpSpent={sessionGiftXpSpent}
              setSessionGiftXpSpent={setSessionGiftXpSpent}
            />
          </div>
        </>
      )}
      {showInstructionModal ? (
        <Modal
          showModal={showInstructionModal}
          setShowModal={setShowInstructionModal}
        >
          <InstructionModalContent
            buttonFunction={() => {
              setShowInstructionModal(false);
            }}
          />
        </Modal>
      ) : null}
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
