import React from "react";

import "../../styles.css";

import Message from "./Message";
import MissionCompleteMessage from "./MissionCompleteMessage";
import SettingMessage from "./SettingMessage";
import SoulSpawnEventMessage from "./SoulSpawnEventMessage";

function get_msg_actor(msg) {
  if (msg.actors === undefined) {
    return msg.actor.node_id;
  } else {
    return msg.actors[0];
  }
}

const Entry = ({
  msg,
  onReply,
  agents,
  selfId,
  setPlayerXp,
  setPlayerGiftXp,
  playerGiftXp,
  playerXp,
  sessionGiftXpSpent,
  setSessionGiftXpSpent,
}) => {
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
      <>
        <MissionCompleteMessage xp={50} name="I want spoon!" />
        {msg.caller == "SoulSpawnEvent" ? (
          <SoulSpawnEventMessage text={msg.text} />
        ) : msg.questComplete ? (
          <MissionCompleteMessage />
        ) : (
          <Message
            text={msg.text}
            isSelf={msg.is_self || actor === selfId}
            actor={agents[actor]}
            onReply={onReply}
            xp={msg.xp}
            actorId={actor}
            eventId={msg.event_id}
            playerGiftXp={playerGiftXp}
            setPlayerGiftXp={setPlayerGiftXp}
            sessionGiftXpSpent={sessionGiftXpSpent}
            setSessionGiftXpSpent={setSessionGiftXpSpent}
          />
        )}
      </>
    );
  }
};
export default Entry;
