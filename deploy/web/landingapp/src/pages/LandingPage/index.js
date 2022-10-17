/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useCallback, useEffect, Fragment } from "react";
/* CUSTOM COMPONENTS */
import ChatDisplay from "./ChatDisplay";
/* IMAGES */
import Scribe from "../../assets/images/scribe.png";
import "./styles.css";

const LandingPage = () => {
  /*---------------LOCAL STATE----------------*/
  //CHAT TEXT STATE
  const [messages, setMessages] = useState([]);
  //CHAT INPUT TEXT
  const [chatInputText, setChatInputText] = useState("");
  //INPUT ACTION TYPE
  const [inputActionType, setInputActionType] = useState("say");
  //SUBMITTED ACTIONS
  const [submittedActions, setSubmittedActions] = useState([]);
  //CHAT DISPLAY REF
  const chatContainerRef = React.useRef(null);
  /*--------------- HANDLERS ----------------*/
  const inputActionTypeToggleHandler = () => {
    if (inputActionType === "say") {
      setInputActionType("do");
    } else {
      setInputActionType("say");
    }
  };
  const inputChangeHandler = (e) => {
    let updatedInputValue = e.target.value;
    setChatInputText(updatedInputValue);
  };

  const chatSubmissionHandler = () => {
    let newChatSubmission = {
      action: inputActionType,
      text: chatInputText,
    };
    let updatedMessages = [...messages, newChatSubmission];
    let updatedSubmittedActions = [newChatSubmission, ...submittedActions];
    setMessages(updatedMessages);
    setSubmittedActions(updatedSubmittedActions);
    setChatInputText("");
    scrollToBottom();
  };
  //SCROLL TO BOTTOM OF DISPLAY CALLBACK
  const scrollToBottom = useCallback(
    () =>
      setTimeout(() => {
        if (chatContainerRef.current)
          chatContainerRef.current.scrollTop =
            chatContainerRef.current.scrollHeight;
      }, 0),
    [chatContainerRef]
  );
  return (
    <>
      <div className="_sidebar-container_ flex-1 relative">
        <div className="w-1/4 " />
      </div>
      <div className="_chat-container_ flex-1 grow-[3] h-full">
        <ChatDisplay
          chatInputText={chatInputText}
          inputActionType={inputActionType}
          inputActionTypeToggleHandler={inputActionTypeToggleHandler}
          inputChangeHandler={inputChangeHandler}
          scrollToBottom={scrollToBottom}
          messages={messages}
          submittedActions={submittedActions}
          onSubmit={chatSubmissionHandler}
          chatContainerRef={chatContainerRef}
        />
      </div>
    </>
  );
};

export default LandingPage;
