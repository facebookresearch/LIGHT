/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* CUSTOM COMPONENTS */
import ChatButtons from "./ChatButtons";
import ChatInput from "./ChatInput";
import SendButton from "./SendButton";
/* UTILS */
import { getActionThemeColor } from "../../../../../app/theme";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatBar = ({
  introStep,
  submittedActions,
  onSubmit,
  scrollToBottom,
  inputChangeHandler,
  inputActionTypeToggleHandler,
  inputActionType,
  chatInputText,
}) => {
  /*---------------LOCAL STATE----------------*/
  const [cycleMessagesPosition, setCycleMessagesPosition] = useState(0);
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    setCycleMessagesPosition(submittedActions.length);
  }, [submittedActions]);

  return (
    <div
      className={`_chat-bar_ w-full rounded ${getActionThemeColor(
        "border",
        inputActionType
      )} border-2 p-2`}
    >
      <div className="flex flex-row items-stretch h-[45px]">
        <div className="flex-0">
          {introStep >= 2 ? (
            <ChatButtons
              toggleAction={inputActionTypeToggleHandler}
              action={inputActionType}
            />
          ) : null}
        </div>
        <div className="flex-1 flex items-center">
          <ChatInput
            inputChangeHandler={inputChangeHandler}
            chatInputText={chatInputText}
            inputActionTypeToggleHandler={inputActionTypeToggleHandler}
            submittedActions={submittedActions}
            onSubmit={onSubmit}
          />
        </div>
        <div className="flex-0 flex items-center">
          <SendButton
            action={inputActionType}
            scrollToBottom={scrollToBottom}
            onSubmit={onSubmit}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatBar;
