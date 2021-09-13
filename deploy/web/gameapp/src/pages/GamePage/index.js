/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch } from "../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import { updateAgents } from "../../features/agents/agents-slice.ts";
import { updateEmoji } from "../../features/playerInfo/emoji-slice";
import { updateLocation } from "../../features/playerInfo/location-slice.ts";
import { updatePersona } from "../../features/playerInfo/persona-slice.ts";
import { updateXp } from "../../features/playerInfo/xp-slice.ts";
import { updateGiftXp } from "../../features/playerInfo/giftxp-slice.ts";
import { updateSessionXp } from "../../features/sessionInfo/sessionxp-slice";
import { updateSessionSpentGiftXp } from "../../features/sessionInfo/sessionspentgiftxp-slice";
//STYLES
import "../../styles.css";
import "./styles.css";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";
//EMOJI
import { DefaultEmojiMapper } from "../../utils";
import { Picker, emojiIndex } from "emoji-mart";
import onClickOutside from "react-onclickoutside";
//CUSTOM COMPONENTS
import { useWSDataSource } from "../../WebSockets/useWSDataSource";
import MobileFrame from "../../components/MobileFrame";
import LoadingPage from "../../pages/LoadingPage";
import Sidebar from "./Sidebar";
import ChatDisplay from "./ChatDisplay";
import Modal from "../../components/Modal";
import InstructionModalContent from "./InstructionModalContent";
//CONFIG
import CONFIG from "../../config.js";

//WEBSOCKECT CONNECTION FUNCTION
const createWebSocketUrlFromBrowserUrl = (url) => {
  console.log("URL", url);
  const wsProtocol = url.protocol === "https:" ? "wss" : "ws";
  console.log("wsProtocol", wsProtocol);
  const optionalServerHost = new URL(url).searchParams.get("server");
  console.log("optionalServerHost", optionalServerHost);
  var optionalGameId = new URL(url).searchParams.get("id");
  console.log("optionalGameId", optionalGameId);
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
  console.log("WS URL", websocketURL, "CONFIG", CONFIG);
  return websocketURL;
};

//MODEL ADDRESS HELPER FUNCTION
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
    return <LoadingPage isFull={isFull} />;
  }
  console.log("PERSONA", persona);
  console.log("AGENTS", agents);
  console.log("LOCATION", location);
  console.log("MESSSAGES", messages);
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
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
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
    const { xp, giftXp } = persona;
    /* ----PLAYER INFO---- */
    dispatch(updatePersona(persona));
    dispatch(updateXp(xp));
    dispatch(updateGiftXp(giftXp));
    //Show Tutorial Modal condition
    let characterEmoji = DefaultEmojiMapper(persona.name);
    if (persona === null || persona.name === null) return;
    const skipWords = ["a", "the", "an", "of", "with", "holding"];
    const tryPickEmojis = !persona
      ? []
      : emojiIndex.search(characterEmoji).map((o) => {
          return o.native;
        });
    const autopickedEmoji = tryPickEmojis.length > 0 ? tryPickEmojis[0] : "?";
    dispatch(updateEmoji(autopickedEmoji));
    /* ---- INSTRUCTION MODAL---- */
    if (xp <= 10) {
      setShowInstructionModal(true);
    }
    /* ----SESSION INFO---- */
    /* SESSION XP */
    let sessionXpUpdate = 0;
    messages.map((message) => {
      if (message.is_self && message.xp > 0) {
        sessionXpUpdate += message.xp;
      }
    });
    dispatch(updateSessionXp(sessionXpUpdate));
  }, [persona]);

  React.useEffect(() => {
    dispatch(updateLocation(location));
  }, [location]);

  React.useEffect(() => {
    dispatch(updateAgents(agents));
  }, [agents]);

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

  const defaultEmoji = "❓";
  //const { presentAgents } = getLocationState(messages);
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
    setPlayerXp(xp + sessionXp);
    let sessionGiftXpUpdate = sessionXp / 4;
    if (sessionGiftXpUpdate >= 1) {
      setPlayerGiftXp(giftXp + sessionGiftXpUpdate - sessionGiftXpSpent);
    } else {
      setPlayerGiftXp(giftXp - sessionGiftXpSpent);
    }
  }, [sessionXp, sessionGiftXpSpent]);

  /* ----------VIEW--------- */
  /* SCREEN SIZE */
  const updateDimensions = () => {
    setScreenSize(window.innerWidth);
  };
  /* MOBILE */
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

  /* DRAWER */
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
