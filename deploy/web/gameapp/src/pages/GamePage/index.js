/* REACT */
import React, { useEffect, Fragment } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import { updateAgents } from "../../features/agents/agents-slice.ts";
import { updateEmoji } from "../../features/playerInfo/emoji-slice";
import { updateLocation } from "../../features/playerInfo/location-slice.ts";
import { updatePersona } from "../../features/playerInfo/persona-slice.ts";
import { updateXp } from "../../features/playerInfo/xp-slice.ts";
import { updateGiftXp } from "../../features/playerInfo/giftxp-slice.ts";
import { updateSessionXp } from "../../features/sessionInfo/sessionxp-slice";
import { updateIsMobile } from "../../features/view/view-slice";
import { setReportModal } from "../../features/modals/modals-slice";
/* STYLES */
import { Dialog, Transition } from "@headlessui/react";
import "./styles.css";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";
/* EMOJI */
import { DefaultEmojiMapper } from "../../utils";
import { emojiIndex } from "emoji-mart";
/* CUSTOM COMPONENTS */
import { useWSDataSource } from "../../WebSockets/useWSDataSource";
import MobileFrame from "../../components/MobileFrame";
import LoadingPage from "../../pages/LoadingPage";
import Sidebar from "./Sidebar";
import ChatDisplay from "./ChatDisplay";
/* CONFIG */
import CONFIG from "../../config.js";

//WEBSOCKET CONNECTION FUNCTION
const createWebSocketUrlFromBrowserUrl = (url) => {
  //console.log("URL", url);
  const wsProtocol = url.protocol === "https:" ? "wss" : "ws";
  //console.log("wsProtocol", wsProtocol);
  const optionalServerHost = new URL(url).searchParams.get("server");
  //console.log("optionalServerHost", optionalServerHost);
  var optionalGameId = new URL(url).searchParams.get("id");
  //console.log("optionalGameId", optionalGameId);
  if (!optionalGameId) {
    optionalGameId = "";
  }
  if (optionalServerHost) {
    console.log("Using user-provided server hostname:", optionalServerHost);
  }

  let websocketURL =
    wsProtocol + "://" + (optionalServerHost || CONFIG.hostname);
  if (CONFIG.port !== "80") {
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

//ConnectedApp - Creates socket and renders Chat Component upon successful connection to backend.
const ConnectedApp = () => {
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
};

//Chat - Renders game all all visual components
const Chat = ({
  messages,
  onSubmit,
  persona,
  location,
  agents,
  disconnectFromSession,
}) => {
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //MODAL STATE
  const showReportModal = useAppSelector(
    (state) => state.modals.showReportModal
  );
  //GIFT XP STATE
  const giftXp = useAppSelector((state) => state.giftXp.value);
  //SESSION XP STATE
  const sessionXp = useAppSelector((state) => state.sessionXp.value);
  //SESSION GIFT XP STATE
  const sessionGiftXpSpent = useAppSelector(
    (state) => state.sessionSpentGiftXp.value
  );
  //MOBILE STATE
  const isMobile = useAppSelector((state) => state.view.isMobile);
  //DRAWER
  const showDrawer = useAppSelector((state) => state.view.showDrawer);
  /* REDUX ACTIONS */
  const selectEmoji = (emoji) => dispatch(updateEmoji(emoji));

  /* ------ LOCAL STATE ------ */
  const [screenSize, setScreenSize] = React.useState(null);
  //IDLE STATE
  const [idleTime, setIdleTime] = React.useState(0);
  const [idle, setIdle] = React.useState(false);
  //CHAT TEXT STATE
  const chatContainerRef = React.useRef(null);
  // AGENT AND CHARACTER STATE
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

  const getLocationState = (messages) => {
    var valid_messages = messages.filter(
      (m) => m.is_self !== true && m.caller !== null
    );
    if (valid_messages.length === 0) return [null, []];
    var lastMessage = valid_messages[valid_messages.length - 1];
    return {
      currentRoom: lastMessage.room_id,
      presentAgents: Object.keys(lastMessage.present_agent_ids),
    };
  };

  /*------REDUX ACTIONS--------*/
  const openReportModal = () => {
    dispatch(setReportModal(true));
  };

  const closeReportModal = () => {
    dispatch(setReportModal(false));
  };

  /* PLAYER AND SESSION INFO UPDATES TO REDUX STORE */
  useEffect(() => {
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
      //NEW Tutorial triggers
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

  useEffect(() => {
    dispatch(updateGiftXp(giftXp - sessionGiftXpSpent));
  }, [sessionGiftXpSpent]);
  /* LOCATION UPDATES TO REDUX STORE */
  useEffect(() => {
    dispatch(updateLocation(location));
  }, [location]);

  /* AGENT UPDATES TO REDUX STORE */
  useEffect(() => {
    dispatch(updateAgents(agents));
  }, [agents]);

  /* IDLE TIMER */
  useEffect(() => {
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

  // SCROLL TO BOTTOM UPON RECIEVING NEW MESSAGES
  useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom, messages]);

  //const { presentAgents } = getLocationState(messages);

  useEffect(() => {
    const defaultEmoji = "❓";
    let characterEmoji = DefaultEmojiMapper(persona.name);
    if (characterEmoji === undefined) {
      characterEmoji = persona.name;
    }
    if (persona === null || persona.name === null) return;
    //const skipWords = ["a", "the", "an", "of", "with", "holding"];
    const tryPickEmojis = !persona
      ? []
      : emojiIndex.search(characterEmoji).map((o) => {
          return o.native;
        });
    const autopickedEmoji =
      tryPickEmojis.length > 0 ? tryPickEmojis[0] : defaultEmoji;
    selectEmoji(autopickedEmoji);
  }, [persona]);

  /* SESSION AND GIFT XP UPDATE PLAYER XP and GIFT XP */
  useEffect(() => {
    const { xp, giftXp } = persona;
    dispatch(updateXp(xp + sessionXp));
    let sessionGiftXpUpdate = sessionXp / 4;
    if (sessionGiftXpUpdate >= 1) {
      dispatch(updateGiftXp(giftXp + sessionGiftXpUpdate - sessionGiftXpSpent));
    } else {
      dispatch(updateGiftXp(giftXp - sessionGiftXpSpent));
    }
  }, [sessionXp, sessionGiftXpSpent]);

  /* ----------VIEW--------- */
  /* SCREEN SIZE */
  const updateDimensions = () => {
    setScreenSize(window.innerWidth);
  };
  /* MOBILE */
  useEffect(() => {
    window.addEventListener("resize", updateDimensions);
    let startingSize = window.innerWidth;
    if (startingSize <= 950) {
      dispatch(updateIsMobile(true));
    } else if (startingSize > 950) {
      dispatch(updateIsMobile(false));
    }
  });

  useEffect(() => {
    if (screenSize <= 950) {
      dispatch(updateIsMobile(true));
    } else if (screenSize > 950) {
      dispatch(updateIsMobile(false));
    }
  }, [screenSize]);

  const buttons = [];

  /* ----------TAILWIND CLASSES--------- */
  const classNames = {
    gamepageContainer: "container h-full max-h-full",
  };
  return (
    <div className={classNames.gamepageContainer} onMouseMove={resetIdleTimer}>
      {isMobile ? (
        <MobileFrame buttons={buttons}>
          {persona ? (
            <Sidebar
              dataModelHost={dataModelHost}
              getEntityId={getEntityId}
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
          />
        </MobileFrame>
      ) : (
        <div className="flex h-screen">
          <div className="w-1/4">
            {persona ? (
              <Sidebar
                dataModelHost={dataModelHost}
                getEntityId={getEntityId}
              />
            ) : (
              <div />
            )}
          </div>
          <div className=" w-3/4">
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
        </div>
      )}
      <Transition.Root show={showReportModal} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={closeReportModal}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          ></Transition.Child>

          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enterTo="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 translate-y-0 sm:scale-100"
            leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <Dialog.Panel className="relative bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-sm sm:w-full sm:p-6">
              <Dialog.Title
                as="h3"
                className="text-lg leading-6 font-medium text-gray-900"
              ></Dialog.Title>
            </Dialog.Panel>
          </Transition.Child>
        </Dialog>
      </Transition.Root>
    </div>
  );
};

export default ConnectedApp;
