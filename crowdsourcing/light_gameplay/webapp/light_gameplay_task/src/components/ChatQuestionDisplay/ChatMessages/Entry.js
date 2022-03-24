/* REACT */
import React from "react";
/* MESSAGE COMPONENTS */
import PlayerMessage from "./PlayerMessage";
import AgentMessage from "./AgentMessage";
import QuestMessage from "./QuestMessage";

//Entry - Renders specific type of message component based on individual message object's attributes
const Entry = ({
  msg,
  speaker,
  isPlayer,
}) => {

  if (isPlayer) {
    return (
          <PlayerMessage
            text={msg.text}
            speaker={speaker}
          />
        )
  } else {
    return (
          <AgentMessage
            text={msg.text}
            speaker={speaker}
          />
        )
  }
};

export default Entry;
