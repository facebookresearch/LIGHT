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
import ActionBar from "../ActionBar";
import DisconnectMessage from "./DisconnectMessage";

//ChatControls - render container that holds both chat input and "action bar" which contains quick chat speech bubbles for each npc in vincinity
const ChatControls = ({
  presentAgents,
  getAgentName,
  getEntityId,
  dataModelHost,
  onSubmit,
  scrollToBottom,
  idle,
  resetIdleTimer,
}) => {
  /* ----------TAILWIND CLASSES--------- */
  const classNames = {
    controls: " w-full",
  };

  return (
    <div className={classNames.controls}>
      {idle ? (
        <DisconnectMessage />
      ) : (
        <>
          <ChatBar
            onSubmit={onSubmit}
            scrollToBottom={scrollToBottom}
            resetIdleTimer={resetIdleTimer}
          />
        </>
      )}
    </div>
  );
};

export default ChatControls;
