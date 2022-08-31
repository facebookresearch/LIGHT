/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useEffect, useState, useCallback, useRef } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { updateSelectedTip } from "../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import ActionBar from "./ActionBar";
import ChatMessages from "./ChatMessages";
import ChatControls from "./ChatControls";
import TutorialPopover from "../../../components/TutorialPopover";
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
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  const persona = useAppSelector((state) => state.persona);
  //PLAYER XP STATE
  const xp = useAppSelector((state) => state.xp.value);
  //SESSION XP STATE
  const sessionXp = useAppSelector((state) => state.sessionXp.value);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    dispatch(updateSelectedTip(tipNumber));
  };
  /* LOCAL STATE */
  const [nonPlayerAgents, setNonPlayerAgents] = useState([]);
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

  useEffect(() => {
    const { presentAgents } = getLocationState(messages);
    let updatedNonPlayerAgents = presentAgents.filter(
      (id) => id !== persona.id
    ); // only show users other than self
    setNonPlayerAgents(updatedNonPlayerAgents);
  }, [messages]);
  /* ----------TAILWIND CLASSES--------- */
  const classNames = {
    chatWrapper: " w-full bg-indigo-900 bg-opacity-50 	overflow-y-hidden ",
    chat: "flex flex-col w-full h-5/6 overflow-y-scroll",
  };
  const { presentAgents } = getLocationState(messages);
  return (
    <div className="h-screen">
      {nonPlayerAgents.length ? (
        <div className="h-14 overflow-y-scroll">
          <ActionBar
            presentAgents={nonPlayerAgents}
            getAgentName={getAgentName}
            getEntityId={getEntityId}
            dataModelHost={dataModelHost}
          />
        </div>
      ) : null}
      <div className={`${classNames.chatWrapper} h-full`}>
        <div className={classNames.chat} ref={chatContainerRef}>
          <ChatMessages messages={messages} scrollToBottom={scrollToBottom} />
        </div>
        <div className="h-1/5">
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
          <div className="flex justify-end">
            <p className=" text-gray-200">XP earned this scene:{sessionXp}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatDisplay;
