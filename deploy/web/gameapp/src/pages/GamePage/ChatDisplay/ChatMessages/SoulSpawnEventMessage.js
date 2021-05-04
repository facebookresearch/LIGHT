import React, { useState } from "react";

import { Tooltip } from "react-tippy";

const SoulSpawnEventMessage = ({
  text,
  caller,
  actor,
  isSelf,
  onReply,
  setPlayerXp,
  setPlayerGiftXp,
  playerGiftXp,
  playerXp,
  xp,
  eventId,
  actorId,
  sessionGiftXpSpent,
  setSessionGiftXpSpent,
}) => {
  let SpawnArr = text.split("\n");
  let StarShine1 = SpawnArr[0];
  let Character = SpawnArr[1];
  let Description = SpawnArr[3];
  let Mission = SpawnArr[4];
  let MissionArr = Mission.split(":");
  let MissionDesc = MissionArr[1];

  return (
    <div id="soulspawn" className="soulspawn-container message type-setting">
      <p className="soulspawn-text soulspawn-star">{StarShine1}</p>
      <p className="soulspawn-header">Let there be LIGHT</p>
      <h5 className="soulspawn-subheader">YOUR CHARACTER</h5>
      <p className="soulspawn-text">{Character}</p>
      <p></p>
      <p className="soulspawn-text" style={{ padding: "0 3em 0 3em" }}>
        {Description}
      </p>
      <h5 className="soulspawn-subheader">YOUR MISSION</h5>
      <p className="soulspawn-text">{MissionDesc}</p>
      <p className="soulspawn-text soulspawn-star">{StarShine1}</p>
    </div>
  );
};
export default SoulSpawnEventMessage;
