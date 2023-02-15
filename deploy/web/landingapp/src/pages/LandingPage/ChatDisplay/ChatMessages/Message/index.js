/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* MESSAGE COMPONENTS */
import PlayerMessage from "./MessageTypes/PlayerMessage";
import AgentMessage from "./MessageTypes/AgentMessage";

//Message - Renders specific type of message component based on individual message object's attributes
const Message = ({
  introStep,
  msg,
  onReply,
  scrollToBottom,
  ratingStepHandler,
}) => {
  console.log("MESSAGE:  ", msg)
  return (
    <>
      {msg.isSelf ? (
        <PlayerMessage text={msg.text} action={msg.action} />
      ) : (
        <AgentMessage
          introStep={introStep}
          text={msg.text}
          action={msg.action}
          actor={msg.actor}
          ratingStepHandler={ratingStepHandler}
          scrollToBottom={scrollToBottom}
        />
      )}
    </>
  );
};

export default Message;
