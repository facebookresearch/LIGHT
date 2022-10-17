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
const Message = ({ msg, onReply, scrollToBottom }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;

  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION

  return (
    <>
      {msg.is_self || actor === selfId ? (
        <PlayerMessage
          text={msg.text}
          isSelf={msg.is_self || actor === selfId}
          caller={msg.caller}
          actor={agents[actor]}
          onReply={onReply}
          xp={msg.xp}
          onClickFunction={() => setSelectedTip(17)}
        />
      ) : (
        <AgentMessage
          text={msg.text}
          actor={agents[actor]}
          onReply={onReply}
          xp={msg.xp}
          actorId={actor}
          eventId={msg.event_id}
          onClickFunction={() => setSelectedTip(16)}
          scrollToBottom={scrollToBottom}
        />
      )}
    </>
  );
};

export default Message;
