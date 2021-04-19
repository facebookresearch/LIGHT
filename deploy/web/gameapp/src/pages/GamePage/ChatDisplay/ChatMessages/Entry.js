import React from "react";

import "../../styles.css";

import Message from "./Message";
import SettingMessage from "./SettingMessage";

function get_msg_actor(msg) {
  if (msg.actors === undefined) {
    return msg.actor.node_id;
  } else {
    return msg.actors[0];
  }
}

const Entry = ({ msg, onReply, agents, selfId }) => {
  console.log("MESSAGE RESPONSE", msg);
  if (
    [
      "LookEvent",
      "GoEvent",
      "ExamineEvent",
      "ErrorEvent",
      "HelpEvent",
      "text",
    ].includes(msg.caller) ||
    msg.caller === null
  ) {
    return <SettingMessage text={msg.text} />;
  } else {
    var actor = get_msg_actor(msg);
    return (
      <Message
        text={msg.text}
        isSelf={msg.is_self || actor === selfId}
        actor={agents[actor]}
        onReply={onReply}
      />
    );
  }
};
export default Entry;
