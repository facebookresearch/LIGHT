/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useEffect, useCallback, useRef } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { updateSelectedTip } from "../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
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
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    dispatch(updateSelectedTip(tipNumber));
  };
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

  const { presentAgents } = getLocationState(messages);
  return (
    <div className="chat-wrapper">
      <div className="chat" ref={chatContainerRef}>
        <ChatMessages messages={messages} />
      </div>
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
    </div>
  );
};

export default ChatDisplay;
