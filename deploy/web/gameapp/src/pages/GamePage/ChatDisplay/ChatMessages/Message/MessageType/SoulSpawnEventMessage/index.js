/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REDUX */
import { useAppSelector } from "../../../../../../../app/hooks";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../../components/TutorialPopover";

//SoulSpawnEventyMessage - renders soul spawn event bubbles and formats text for that event
const SoulSpawnEventMessage = ({ text, onClickFunction }) => {
  let SpawnArr = text.split("\n");
  let StarShine1 = SpawnArr[0];
  let Character = SpawnArr[1];
  let Description = SpawnArr[3];
  let Mission = SpawnArr[4];
  let MissionArr = Mission.split(":");
  let MissionDesc = MissionArr[1];

  /* ----REDUX STATE---- */
  //TUTORIAL
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  return (
    <div className="w-full flex justify-center item-center mb-4">
      <TutorialPopover
        tipNumber={9}
        open={inHelpMode && selectedTip === 9}
        position="bottom"
      >
        <div
          className={`${
            inHelpMode ? "active" : ""
          } flex justify-center items-center p-4`}
        >
          <div
            className={`  text-white text-center text-md`}
            onClick={onClickFunction}
          >
            {/* <p className=" _soulspawn-stars_">{StarShine1}</p> */}
            <p className="soulspawn-header">Let there be LIGHT</p>
            <p className="soulspawn-text">{Character}</p>
            <p></p>
            <h5 className="soulspawn-subheader">YOUR CHARACTER</h5>
            <p className="soulspawn-text" style={{ padding: "0 3em 0 3em" }}>
                {Description}
            </p>
            <h5 className="soulspawn-subheader">YOUR MISSION</h5>
            <p className="soulspawn-text">{MissionDesc}</p>
            <p className="soulspawn-text">
              You will be rewarded for roleplaying so play your character to the
              best of your ability.
            </p>
            {/* <p className="soulspawn-text soulspawn-star">{StarShine1}</p> */}
          </div>
        </div>
      </TutorialPopover>
    </div>
    // <div
    //   id="soulspawn"
    //   className={`soulspawn-container ${inHelpMode ? "active" : ""}`}
    //   onClick={onClickFunction}
    // >
    /* <p className="soulspawn-text soulspawn-star">{StarShine1}</p>
      <p className="soulspawn-header">Let there be LIGHT</p>
      <p className="soulspawn-text">{Character}</p>
      <p></p>
      <h5 className="soulspawn-subheader">YOUR CHARACTER</h5>
      <p className="soulspawn-text" style={{ padding: "0 3em 0 3em" }}>
        <TutorialPopover
          tipNumber={9}
          open={inHelpMode && selectedTip === 9}
          position="bottom"
        >
          {Description}
        </TutorialPopover>
      </p>
      <h5 className="soulspawn-subheader">YOUR MISSION</h5>
      <p className="soulspawn-text">{MissionDesc}</p>
      <p className="soulspawn-text">
        You will be rewarded for roleplaying so play your character to the best
        of your ability.
      </p>
      <p className="soulspawn-text soulspawn-star">{StarShine1}</p>
       */
  );
};
export default SoulSpawnEventMessage;
