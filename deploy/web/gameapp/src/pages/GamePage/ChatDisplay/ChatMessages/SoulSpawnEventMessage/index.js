/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//SoulSpawnEventyMessage - renders soul spawn event bubbles and formats text for that event
const SoulSpawnEventMessage = ({ text }) => {
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
      <p className="soulspawn-text">{Character}</p>
      <p></p>
      <h5 className="soulspawn-subheader">YOUR CHARACTER</h5>
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
