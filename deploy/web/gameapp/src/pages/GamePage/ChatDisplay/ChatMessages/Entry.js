import React from "react";

import Message from "./Message";
import InventoryMessage from "./InventoryMessage";
import MissionCompleteMessage from "./MissionCompleteMessage";
import HelpMessage from "./HelpMessage";
import SettingMessage from "./SettingMessage";
import SoulSpawnEventMessage from "./SoulSpawnEventMessage";
import StatusMessage from "./StatusMessage";
import QuestMessage from "./QuestMessage";

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
      "InventoryEvent",
      "HealthEvent",
      "QuestEvent",
    ].includes(msg.caller) ||
    msg.caller === null
  ) {
    if (msg.caller == "HelpEvent") {
      return <HelpMessage text={msg.text} />;
    } else if (msg.caller == "InventoryEvent") {
      return <InventoryMessage text={msg.text} />;
    } else if (msg.caller == "HealthEvent") {
      return <StatusMessage text={msg.text} />;
    } else if (msg.caller == "QuestEvent") {
      return <QuestMessage text={msg.text} />;
    } else {
      return <SettingMessage text={msg.text} />;
    }
  } else {
    var actor = get_msg_actor(msg);
    return (
      <>
        {msg.caller == "SoulSpawnEvent" ? (
          <SoulSpawnEventMessage text={msg.text} />
        ) : msg.questComplete ? (
          <MissionCompleteMessage xp={msg.xp} name={msg.text} />
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
