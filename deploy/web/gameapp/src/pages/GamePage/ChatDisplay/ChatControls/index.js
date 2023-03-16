/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import ChatBar from "./ChatBar";
import DisconnectMessage from "./DisconnectMessage";

//ChatControls - render container that holds both chat input and "action bar" which contains quick chat speech bubbles for each npc in vincinity
const ChatControls = ({
  onSubmit,
  scrollToBottom,
  idle,
  resetIdleTimer,
  chatInputRef,
  autoScrollToBottom,
}) => {
  return (
    <div className="_chat-controls_ w-full">
      {idle ? (
        <DisconnectMessage />
      ) : (
        <>
          <ChatBar
            onSubmit={onSubmit}
            scrollToBottom={scrollToBottom}
            resetIdleTimer={resetIdleTimer}
            chatInputRef={chatInputRef}
            autoScrollToBottom={autoScrollToBottom}
          />
        </>
      )}
    </div>
  );
};

export default ChatControls;
