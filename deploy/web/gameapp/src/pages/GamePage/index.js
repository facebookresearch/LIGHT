/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useCallback, useEffect, Fragment } from "react";
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
import { updateSessionSpentGiftXp } from "../../features/sessionInfo/sessionspentgiftxp-slice";
import { updateSessionEarnedGiftXp } from "../../features/sessionInfo/sessionearnedgiftxp-slice";
import { updateIsMobile } from "../../features/view/view-slice";
import { setReportModal } from "../../features/modals/modals-slice";
/* STYLES */
import "./styles.css";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";
/* IMAGES */
import StarryNight from "../../assets/images/light_starry_bg.jpg";
/* EMOJI */
import { DefaultEmojiMapper } from "../../utils";
import { emojiIndex } from "emoji-mart";
/* CUSTOM COMPONENTS */
import { useWSDataSource } from "../../WebSockets/useWSDataSource";
import MobileFrame from "../../components/MobileFrame";
import LoadingPage from "../../pages/LoadingPage";
import Sidebar from "./Sidebar";
import SideDrawer from "../../components/SideDrawer";
import MobileDrawer from "../../components/MobileDrawer";
import ChatDisplay from "./ChatDisplay";
import ReportMessageModal from "../../components/Modals/ReportMessageModal";
/* ICONS */
import { BiRightArrow } from "react-icons/bi";

/* CONFIG */
import CONFIG from "../../config.js";
// import { Console } from "console";

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
    markPlayerAsIdle,
    isIdle,
  } = useWSDataSource(wsUrl);

  if (isErrored && !isIdle)
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
      markPlayerAsIdle={markPlayerAsIdle}
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
  markPlayerAsIdle,
}) => {
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //MODAL STATE
  const showReportModal = useAppSelector(
    (state) => state.modals.showReportModal
  );
  //XP State
  const xp = useAppSelector((state) => state.xp.value);
  //GIFT XP STATE
  const giftXp = useAppSelector((state) => state.giftXp.value);
  //SESSION XP STATE
  const sessionXp = useAppSelector((state) => state.sessionXp.value);
  //SESSION GIFT XP STATE
  const sessionGiftXpSpent = useAppSelector(
    (state) => state.sessionSpentGiftXp.value
  );
  const sessionEarnedGiftXp = useAppSelector(
    (state) => state.sessionEarnedGiftXp.value
  );
  //MOBILE STATE
  const isMobile = useAppSelector((state) => state.view.isMobile);
  //DRAWER STATE
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
  //MOBILE DRAWER STATE
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const scrollToBottom = React.useCallback(
    () =>
      setTimeout(() => {
        if (chatContainerRef.current)
          chatContainerRef.current.scrollTop =
            chatContainerRef.current.scrollHeight;
      }, 0),
    [chatContainerRef]
  );
  /* UTILS */
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

  /* HANDLERS */

  /*  LIFE CYCLE */
  /* PLAYER AND SESSION INFO UPDATES TO REDUX STORE */
  useEffect(() => {
    console.log("UPDATED PERSONA", persona);
    if (persona) {
      let updatedXp = persona.xp;
      let updatedGiftXp = persona.giftXp;
      console.log("XP", updatedXp);
      console.log("GIFT XP", updatedGiftXp);
      /* ----PLAYER INFO---- */
      dispatch(updatePersona(persona));
      dispatch(updateXp(updatedXp));
      dispatch(updateGiftXp(updatedGiftXp));
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
      /* ---- INSTRUCTION MODAL---- !!!!!!!!!!!!!!!!!!!!!!!!!*/
      if (updatedXp <= 10) {
        //NEW Tutorial triggers
      }
    }
  }, [persona]);
  useEffect(() => {
    /* ----SESSION INFO---- */
    /* SESSION XP */
    let sessionXpUpdate = 0;
    messages.map((message) => {
      if (message.is_self && message.xp > 0) {
        sessionXpUpdate += message.xp;
      }
    });
    let newSessionXp = sessionXpUpdate - sessionXp;
    let newGiftXp = newSessionXp / 4;
    if (newSessionXp > 0) {
      let updatedXp = sessionXpUpdate;
      dispatch(updateSessionXp(updatedXp));
    }
    if (newGiftXp >= 1) {
      let updatedSessionGiftXpEarned = sessionEarnedGiftXp + newGiftXp;
      dispatch(updateSessionEarnedGiftXp(updatedSessionGiftXpEarned));
    }
  }, [messages]);

  /* UPDATE PLAYER XP */
  useEffect(() => {
    if (sessionXp > 0) {
      let updatedXP = xp + sessionXp;
      dispatch(updateXp(updatedXP));
    }
  }, [sessionXp]);

  //* GIFT XP UPDATES TO REDUX STORE */
  useEffect(() => {
    if (sessionEarnedGiftXp >= 1 || sessionGiftXpSpent >= 1) {
      let updatedGiftXp = giftXp + sessionEarnedGiftXp - sessionGiftXpSpent;
      console.log("Updated GIFT XP:  ", updatedGiftXp);
      dispatch(updateGiftXp(updatedGiftXp));
    }
  }, [sessionEarnedGiftXp, sessionGiftXpSpent]);

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
      markPlayerAsIdle();
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

  /* SESSION GIFT XP */
  useEffect(() => {
    console.log(
      "giftXp sessionGiftXpSpent sessionGiftXpSpent",
      giftXp,
      sessionEarnedGiftXp,
      sessionGiftXpSpent
    );
    if (sessionGiftXpSpent >= 1) {
      dispatch(updateGiftXp(giftXp + sessionEarnedGiftXp - sessionGiftXpSpent));
    }
  }, [sessionGiftXpSpent]);

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

  return (
    <div
      style={{
        backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
      }}
      className="_game-page_ flex h-screen w-screen bg-cover bg-top bg-no-repeat"
      onMouseMove={resetIdleTimer}
    >
      <div className="flex h-screen">
        <div className="flex flex-row h-screen">
          <div className="_sidebar-container_ hidden sm:hidden md:flex md:flex-1 md:relative lg:flex-1 lg:relative xl:flex-1 xl:relative 2xl:flex-1 2xl:relative">
            <Sidebar dataModelHost={dataModelHost} getEntityId={getEntityId} />
          </div>
          <div className="_sidebar-container_ flex sm:flex md:hidden lg:hidden xl:hidden 2xl:hidden">
            <MobileDrawer
              isDrawerOpen={isDrawerOpen}
              closeDrawerFunction={() => setIsDrawerOpen(false)}
              openDrawerFunction={() => setIsDrawerOpen(true)}
            >
              <Sidebar
                dataModelHost={dataModelHost}
                getEntityId={getEntityId}
              />
            </MobileDrawer>
          </div>
          {/* <div className="_sidebar-container_ flex-1 relative">
            {showDrawer ? <SideDrawer /> : null}
            {persona ? (
              <Sidebar
                dataModelHost={dataModelHost}
                getEntityId={getEntityId}
              />
            ) : (
              <div />
            )}
          </div> */}
          <div className="_chat-container_ flex-1 md:grow-[3] lg:grow-[3] xl:grow-[3] 2xl:grow-[3] h-full">
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
      </div>
      <ReportMessageModal />
    </div>
  );
};

export default ConnectedApp;

// <div
// style={{ backgroundImage: `url(${StarryNight})` }}
// className={classNames.gamepageContainer}
// onMouseMove={resetIdleTimer}
// >
// {isMobile ? (
//   <MobileFrame buttons={buttons}>
//     {persona ? (
//       <Sidebar
//         dataModelHost={dataModelHost}
//         getEntityId={getEntityId}
//         isMobile={isMobile}
//         showDrawer={showDrawer}
//       />
//     ) : null}
//     <ChatDisplay
//       scrollToBottom={scrollToBottom}
//       messages={messages}
//       onSubmit={onSubmit}
//       persona={persona}
//       location={location}
//       agents={agents}
//       getDataModelAddress={getDataModelAddress}
//       getLocationState={getLocationState}
//       idle={idle}
//       resetIdleTimer={resetIdleTimer}
//     />
//   </MobileFrame>
// ) : (
//   <div className="flex h-screen">
//     <div className="w-1/4">
//       {persona ? (
//         <Sidebar
//           dataModelHost={dataModelHost}
//           getEntityId={getEntityId}
//         />
//       ) : (
//         <div />
//       )}
//     </div>
//     <div className=" w-3/4">
//       <ChatDisplay
//         scrollToBottom={scrollToBottom}
//         messages={messages}
//         onSubmit={onSubmit}
//         persona={persona}
//         location={location}
//         agents={agents}
//         getDataModelAddress={getDataModelAddress}
//         getLocationState={getLocationState}
//         idle={idle}
//         resetIdleTimer={resetIdleTimer}
//       />
//     </div>
//   </div>
// )}
// <ReportMessageModal />
// </div>
