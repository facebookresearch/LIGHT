/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */

/* CUSTOM COMPONENTS */
import ChatMessages from "./ChatMessages";
import ChatControls from "./ChatControls";

//ChatDisplay - renders primary container for both chat and entirety of chat controls
const ChatDisplay = ({
  introStep,
  ratingStepHandler,
  chatInputText,
  inputActionType,
  inputActionTypeToggleHandler,
  inputChangeHandler,
  scrollToBottom,
  messages,
  submittedActions,
  onSubmit,
  chatContainerRef,
}) => {
  return (
    <div className="__chatdisplay-container__ h-full m-8 flex flex-col">
      <div className="__chatdisplay-chat-container__ flex flex-1 flex-col h-full bg-indigo-900 bg-opacity-50 overflow-hidden p-7 rounded-t-md">
        <div
          className="__chatdisplay-message-container__ flex-1 grow-[5] overflow-y-scroll"
          ref={chatContainerRef}
        >
          {messages ? (
            <ChatMessages
              introStep={introStep}
              messages={messages}
              ratingStepHandler={ratingStepHandler}
              scrollToBottom={scrollToBottom}
            />
          ) : null}
        </div>
        <div className="__chatdisplay-chatcontrols-container__ flex-none h-[120px]">
          {introStep >= 1 ? (
            <ChatControls
              introStep={introStep}
              submittedActions={submittedActions}
              onSubmit={onSubmit}
              scrollToBottom={scrollToBottom}
              inputChangeHandler={inputChangeHandler}
              inputActionTypeToggleHandler={inputActionTypeToggleHandler}
              inputActionType={inputActionType}
              chatInputText={chatInputText}
            />
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default ChatDisplay;
