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

//LandingPage - Renders the Landing Page.  This page renders elements based on stepping through the postLoginSteps.
//*
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
  //postLoginStepIncreaseHandler - iterates through postLoginSteps which triggers different elements to render
  const postLoginStepIncreaseHandler = () => {
    let nextStep = postLoginStep + 1;
    setPostLoginStep(nextStep);
  };

  //inputActionTypeToggleHandler - toggles between say and do inputAction state
  const inputActionTypeToggleHandler = () => {
    if (inputActionType === "say") {
      setInputActionType("do");
    } else {
      setInputActionType("say");
    }
  };

  //inputChangeHandler - sets text of chat input.
  const inputChangeHandler = (e) => {
    let updatedInputValue = e.target.value;
    setChatInputText(updatedInputValue);
  };

  //ratingStepHandler - sets intro step upon completion of the rating step in the intro
  const ratingStepHandler = () => {
    setIntroStep(4);
    let updatedMessages = [
      ...messages,
      introDialogueSteps[4],
      introDialogueSteps[5],
      introDialogueSteps[6],
    ];
    setMessages(updatedMessages);
  };

  //chatSubmissionHandler - sets intro step based completion of chat submission steps
  //as well as submits messages to chat display
  const chatSubmissionHandler = () => {
    if (introStep === 4) {
      setIntroStep(5);
    }
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
  //Upon render sets first messages in intro chat display
  useEffect(() => {
    console.log(messages);
    let updatedMessage = [introDialogueSteps[0]];
    setMessages(updatedMessage);
  }, []);

  //Listens for proper message entries rerquired to complete currernt intro step and continue to move through intro and postlogin stepper
  useEffect(() => {
    if (messages.length) {
      let newMessage = messages[messages.length - 1];
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
          let updatedMessage = introDialogueSteps[3];
          let updatedMessages = [...messages, updatedMessage];
          setMessages(updatedMessages);
        }
      }
      if (introStep >= 5) {
        setTimeout(() => {
          const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ completed: true }),
          };
          const loginData = fetch("/submit_intro", requestOptions)
            .then((response) => {
              console.log(response);
              window.location.href = "/play";
            })
            .catch((error) => {
              console.error("There was an error!", error);
            });
        }, 3000);
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
            <div className="">{introStep >= 4 ? <SideBarDisplay /> : null}</div>
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
