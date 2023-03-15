/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* CUSTOM COMPONENTS */
import ChatBar from "./ChatBar";

//ChatControls - render container for chatBar component and any other tools that may be added in the future
const ChatControls = ({
  introStep,
  submittedActions,
  onSubmit,
  scrollToBottom,
  inputChangeHandler,
  inputActionTypeToggleHandler,
  inputActionType,
  chatInputText,
}) => {
  return (
    <div className="w-full">
      <ChatBar
        introStep={introStep}
        submittedActions={submittedActions}
        onSubmit={onSubmit}
        scrollToBottom={scrollToBottom}
        chatInputText={chatInputText}
        inputActionType={inputActionType}
        inputActionTypeToggleHandler={inputActionTypeToggleHandler}
        inputChangeHandler={inputChangeHandler}
      />
    </div>
  );
};

export default ChatControls;
