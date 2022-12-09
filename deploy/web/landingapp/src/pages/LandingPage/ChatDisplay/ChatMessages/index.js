/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */

/* CUSTOM COMPONENTS */
import Message from "./Message";

//ChatMessages - Renders messages in chat display by iterating through message reducer returning Entry components
const ChatMessages = ({
  introStep,
  messages,
  scrollToBottom,
  ratingStepHandler,
}) => {
  return (
    <>
      {messages.map((msg, idx) => (
        <div className="_chat-message_" key={idx}>
          <Message
            introStep={introStep}
            msg={msg}
            ratingStepHandler={ratingStepHandler}
            scrollToBottom={scrollToBottom}
          />
        </div>
      ))}
    </>
  );
};

export default ChatMessages;
