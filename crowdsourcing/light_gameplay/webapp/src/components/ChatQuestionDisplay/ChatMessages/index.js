
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
import Entry from "./Entry";

//ChatMessages - Renders messages in chat display by iterating through message reducer returning Entry components
const ChatMessages = ({
  messages
 }) => {
  return (
    <>
      {messages.map((msg, idx) => (
        <div className="message-row" key={idx}>
          <Entry
            msg={msg.text}
            speaker={msg.speaker}
            isPlayer={msg.player}
          />
        </div>
      ))}
    </>
  );
};

export default ChatMessages;
