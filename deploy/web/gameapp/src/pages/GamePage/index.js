/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {
  useState,
  useEffect,
  useRef,
  useCallback,
  useMemo,
} from "react";
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
import { updateSessionEarnedGiftXp } from "../../features/sessionInfo/sessionearnedgiftxp-slice";
/* STYLES */
import "./styles.css";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";
/* CUSTOM COMPONENTS */
//LOADING PAGE
import LoadingPage from "../../pages/LoadingPage";
//SOCKET
import { useWSDataSource } from "../../WebSockets/useWSDataSource";
import Sidebar from "./Sidebar";
import MobileDrawer from "../../components/MobileDrawer";
import ChatDisplay from "./ChatDisplay";
import ReportMessageModal from "../../components/Modals/ReportMessageModal";

/* CONFIG */
import CONFIG from "../../config.js";
// import { Console } from "console";

//WEBSOCKET CONNECTION FUNCTION
const createWebSocketUrlFromBrowserUrl = (url) => {
  const wsProtocol = url.protocol === "https:" ? "wss" : "ws";
  const optionalServerHost = new URL(url).searchParams.get("server");
  let optionalGameId = new URL(url).searchParams.get("id");
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
  const wsUrl = useMemo(
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
//ERROR PAGE
  if (isErrored && !isIdle)
    return (
      <div className="_connectionerror-container_ h-screen w-screen flex justify-center items-center">
        <div className="_connectionerror-text-container_  justify-center items-center">
          <h1 className="_connectionerror-text_ text_ text-white text-center text-2xl">Could not connect to the server</h1>
        </div>
      </div>
    );
//LOADING PAGE
  if (messages.length === 0) {
    return <LoadingPage isFull={isFull} />;
  }
//GAME PAGE
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
  /* REDUX ACTIONS */
  const selectEmoji = (emoji) => dispatch(updateEmoji(emoji));

  /* ------ LOCAL STATE ------ */
  //IDLE STATE
  const [idleTime, setIdleTime] = useState(0);
  const [idle, setIdle] = useState(false);
  //CHAT TEXT STATE
  const chatContainerRef = useRef(null);
  const chatInputRef = useRef(null);
  // AGENT AND CHARACTER STATE
  const getEntityId = (agent) => agent.match(/\d+$/)[0];
  const dataModelHost = getDataModelAddress();
  //MOBILE DRAWER STATE
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const scrollToBottom = useCallback(
    () =>
      setTimeout(() => {
        if (chatContainerRef.current)
          chatContainerRef.current.scrollTop =
            chatContainerRef.current.scrollHeight;
      }, 0),
    [chatContainerRef]
  );
  /* UTILS */
  // getLocationState - returns current room and other characters in current room
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
  // resetIdleTimer - resets idleness state's current time
  const resetIdleTimer = () => {
    setIdleTime(0);
  };
  /*  LIFE CYCLE */
  /* PLAYER AND SESSION INFO UPDATES TO REDUX STORE */
  useEffect(() => {
    if (persona) {
      let updatedXp = persona.xp;
      let updatedGiftXp = persona.giftXp;
      console.log("PERSONA XP:  ", updatedXp)
      /* ----PLAYER INFO---- */
      dispatch(updatePersona(persona));
      dispatch(updateGiftXp(updatedGiftXp));
      let defaultEmoji = "\u2753"
      if (persona === null || persona.name === null) return;
      let characterEmoji = persona.emoji || defaultEmoji
      selectEmoji(characterEmoji);
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
      if(message.caller === "SoulSpawnEvent"){
        let {actor}= message;
        let initialXp = actor.xp;
        if(initialXp >0){
          sessionXpUpdate += initialXp;
        }
      }
      else if (message.is_self && message.xp > 0 || message.questComplete)  {
        sessionXpUpdate += message.xp;
      }else if (message.is_self && message.caller=== "SayEvent") {
        sessionXpUpdate += 1;
      }
    });
    console.log("SESSION XP UPDATES:  ", sessionXpUpdate)
    let newSessionXp = sessionXpUpdate - sessionXp;
    console.log("newSessionXp:  ", sessionXpUpdate)
    let newGiftXp = newSessionXp / 4;
    if (newSessionXp > 0) {
      let updatedSessionXp = sessionXpUpdate;
      console.log("updatedSessionXp:  ", updatedSessionXp)
      dispatch(updateSessionXp(updatedSessionXp));
    }
    if (newGiftXp >= 1) {
      let updatedSessionGiftXpEarned = sessionEarnedGiftXp + newGiftXp;
      dispatch(updateSessionEarnedGiftXp(updatedSessionGiftXpEarned));
    }
  }, [messages]);

  /* UPDATE PLAYER XP */
  useEffect(() => {

      let updatedXP = sessionXp;
      console.log("TOTAL XP:  ", updatedXP)
      dispatch(updateXp(updatedXP));
  }, [sessionXp]);

  //* GIFT XP UPDATES TO REDUX STORE */
  useEffect(() => {
    if (sessionEarnedGiftXp >= 1 || sessionGiftXpSpent >= 1) {
      let updatedGiftXp = giftXp + sessionEarnedGiftXp - sessionGiftXpSpent;
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
  // Increases Idle time by one ever second and at 300 sets playerIdle state to true and disconnects user from session
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


  // SCROLL TO BOTTOM UPON RECIEVING NEW MESSAGES
  useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom, messages]);

  /* EMOJI */
  useEffect(() => {
    let defaultEmoji = "\u2753"
    if (persona === null || persona.name === null) return;
    let characterEmoji = persona.emoji || defaultEmoji
    selectEmoji(characterEmoji);
  }, [persona]);

  /* SESSION GIFT XP */
  useEffect(() => {
    if (sessionGiftXpSpent >= 1) {
      dispatch(updateGiftXp(giftXp + sessionEarnedGiftXp - sessionGiftXpSpent));
    }
  }, [sessionGiftXpSpent]);

  return (
    <div
      className="_game-page_ w-screen h-screen"
      onMouseMove={resetIdleTimer}
    >
      <div className="_gamepage-container_ w-full h-full flex flex-row ">
        <div className="_game-container_ w-full flex flex-row h-screen">
          <div className="_sidebar-container_ hidden sm:hidden md:flex md:flex-1 md:relative lg:flex-1 lg:relative xl:flex-1 xl:relative 2xl:flex-1 2xl:relative">
            <Sidebar dataModelHost={dataModelHost} getEntityId={getEntityId} />
          </div>
          <div className="_sidebar-mobile-container_ flex sm:flex md:hidden lg:hidden xl:hidden 2xl:hidden">
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
          <div className="_chat-container_ overflow-x-hidden w-full flex-1 sm:flex-1 md:grow-[3] lg:grow-[3] xl:grow-[3] 2xl:grow-[3] h-full">
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
              chatInputRef={chatInputRef}
            />
          </div>
        </div>
      </div>
      <ReportMessageModal />
    </div>
  );
};

export default ConnectedApp;
