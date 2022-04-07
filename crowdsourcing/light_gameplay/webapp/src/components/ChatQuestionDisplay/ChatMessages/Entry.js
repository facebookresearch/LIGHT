/* REACT */
import React from "react";
/* MESSAGE COMPONENTS */
import PlayerMessage from "./PlayerMessage";
import AgentMessage from "./AgentMessage";

//Entry - Renders specific type of message component based on individual message object's attributes
const Entry = ({
  msg,
  speaker,
  isPlayer,
}) => {

  if (isPlayer) {
    return (
          <PlayerMessage
            text={msg}
            speaker={speaker}
          />
        )
  } else {
    return (
          <AgentMessage
            text={msg}
            speaker={speaker}
          />
        )
  }
};

export default Entry;
