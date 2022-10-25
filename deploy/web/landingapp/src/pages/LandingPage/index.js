/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useCallback, useEffect, Fragment } from "react";
/* CUSTOM COMPONENTS */
import ChatDisplay from "./ChatDisplay";
import LegalChecklistDisplay from "./LegalChecklistDisplay";
import SideBarDisplay from "./SideBarDisplay";
/* IMAGES */
import "./styles.css";
/* COPY */
import LANDINGAPPCOPY from "../../LandingAppCopy";

const LandingPage = () => {
  const { legalAgreements, introDialogueSteps } = LANDINGAPPCOPY;
  /*---------------LOCAL STATE----------------*/
  //UI INTRO STEP
  const [postLoginStep, setPostLoginStep] = useState(0);
  //UI INTRO STEP
  const [introStep, setIntroStep] = useState(0);
  //CHAT MESSAGES
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
  const postLoginStepIncreaseHandler = () => {
    let nextStep = postLoginStep + 1;
    setPostLoginStep(nextStep);
  };

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

  const ratingStepHandler = () => {
    setIntroStep(3);
    let updatedMessage = introDialogueSteps[4];
    let updatedMessages = [...messages, updatedMessage];
    setMessages(updatedMessages);
  };

  const chatSubmissionHandler = () => {
    let newChatSubmission = {
      action: inputActionType,
      actor: "YOU",
      text: chatInputText,
      isSelf: true,
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

  /*-------------- LIFECYCLE ----------------*/
  useEffect(() => {
    console.log(messages);
    let updatedMessage = [introDialogueSteps[0]];
    setMessages(updatedMessage);
  }, []);

  useEffect(() => {
    if (messages.length) {
      let newMessage = messages[messages.length - 1];
      console.log("NEW MESSAGE:  ", newMessage);
      console.log("Step Logic");
      if (introStep === 0) {
        setIntroStep(1);
        let updatedMessage = introDialogueSteps[1];
        let updatedMessages = [...messages, updatedMessage];
        setMessages(updatedMessages);
      }
      if (introStep === 1) {
        if (newMessage.action === "say" && newMessage.isSelf) {
          setIntroStep(2);
          let updatedMessage = introDialogueSteps[2];
          let updatedMessages = [...messages, updatedMessage];
          setMessages(updatedMessages);
        }
      }
      if (introStep === 2) {
        if (newMessage.action === "do" && newMessage.isSelf) {
          setIntroStep(3);
          let updatedMessage = introDialogueSteps[2];
          let updatedMessages = [...messages, updatedMessage];
          setMessages(updatedMessages);
        }
      }
    }
  }, [messages, introStep]);

  return (
    <>
      {postLoginStep === 0 ? (
        <div className="flex w-full h-full justify-center  overflow-y-scroll pb-10">
          <LegalChecklistDisplay
            legalAgreements={legalAgreements}
            postLoginStepIncreaseHandler={postLoginStepIncreaseHandler}
          />
        </div>
      ) : null}
      {postLoginStep >= 1 ? (
        <>
          <div className="_sidebar-container_ flex-1 relative">
            <div className="">
              {postLoginStep >= 1 ? <SideBarDisplay /> : null}
            </div>
          </div>
          <div className="_chat-container_ flex-1 grow-[3] h-full">
            {messages ? (
              <ChatDisplay
                introStep={introStep}
                ratingStepHandler={ratingStepHandler}
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
            ) : null}
          </div>
        </>
      ) : null}
    </>
  );
};

export default LandingPage;
