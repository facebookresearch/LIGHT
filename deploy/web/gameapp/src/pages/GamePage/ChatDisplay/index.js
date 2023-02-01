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
  chatInputRef,
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

  const { presentAgents } = getLocationState(messages);
  return (
    <div className="_chatdisplay-container_ w-full h-full flex flex-col ">
      {nonPlayerAgents.length ? (
        <div className="_actionbar-container_ flex-0 pt-4 mb-4">
          <ActionBar
            presentAgents={nonPlayerAgents}
            getAgentName={getAgentName}
            getEntityId={getEntityId}
            dataModelHost={dataModelHost}
            chatInputRef={chatInputRef}
          />
        </div>
      ) : null}
      <div className=" _chatdisplay-chat-container_ w-full flex flex-1 flex-col h-full bg-indigo-900 bg-opacity-50 overflow-hidden p-7 rounded-t-md">
        <div
          className="_chatdisplay-message-container_ max-w-full sm:w-full md:max-w-full flex-1 grow-[5] overflow-y-scroll"
          ref={chatContainerRef}
        >
          <ChatMessages messages={messages} scrollToBottom={scrollToBottom} />
        </div>
        <div className="__chatdisplay-chatcontrols-container__  flex-none md:h-[120px]">
          <ChatControls
            onSubmit={onSubmit}
            presentAgents={presentAgents}
            getAgentName={getAgentName}
            getEntityId={getEntityId}
            dataModelHost={dataModelHost}
            scrollToBottom={scrollToBottom}
            idle={idle}
            resetIdleTimer={resetIdleTimer}
            chatInputRef={chatInputRef}
          />
          <div className="flex justify-end">
            <p className="text-base-100 opacity-80 mt-2 text-xs">
              XP earned in this scene:{" "}
              <strong className="text-warning">{sessionXp}</strong>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatDisplay;
