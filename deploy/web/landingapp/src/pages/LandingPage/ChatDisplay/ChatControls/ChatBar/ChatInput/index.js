/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* CUSTOM COMPONENTS */

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatInput = ({
  inputChangeHandler,
  chatInputText,
  inputActionTypeToggleHandler,
  submittedActions,
  onSubmit,
}) => {
  /*---------------LOCAL STATE----------------*/
  const [cycleMessagesPosition, setCycleMessagesPosition] = useState(0);
  /*---------------LIFECYCLE----------------*/

  return (
    <div className="w-full">
      <input
        autoFocus
        name="chat"
        id="chat"
        autoComplete="off"
        style={{ caretColor: "green" }}
        className={`focus:outline-none bg-transparent chatbox-input text-base-100 w-full bg-transparent border-b-[1px] border-b-transparent px-0 py-2 mx-4 font-sans`}
        placeholder="Something..."
        value={chatInputText}
        onChange={inputChangeHandler}
        onKeyDown={(e) => {
          if (e.key == "`") {
            e.preventDefault();
            inputActionTypeToggleHandler();
          }
          if (e.key == "ArrowUp") {
            e.preventDefault();
            if (submittedMessages.length > 0) {
              let updatedPosition = cycleMessagesPosition - 1;
              if (updatedPosition < 0) {
                updatedPosition = submittedMessages.length - 1;
              }
              setCycleMessagesPosition(updatedPosition);
            }
          }
          if (e.key == "ArrowDown") {
            e.preventDefault();
            if (submittedMessages.length > 0) {
              let updatedPosition = cycleMessagesPosition + 1;
              if (updatedPosition >= submittedMessages.length) {
                updatedPosition = 0;
              }
              setCycleMessagesPosition(updatedPosition);
            }
          }
          if (e.key === "Enter") {
            const prefix = e.target.value.startsWith('"') ? "" : '"';
            const suffix = e.target.value.endsWith('"') ? "" : '"';
            onSubmit(e);
          }
        }}
      />
    </div>
  );
};

export default ChatInput;
