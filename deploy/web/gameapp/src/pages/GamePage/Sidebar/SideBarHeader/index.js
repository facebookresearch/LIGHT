/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
/* ---- REDUCER ACTIONS ---- */
import { useAppSelector, useAppDispatch } from "../../../../app/hooks";
import { updateShowDrawer } from "../../../../features/view/view-slice";
import { updateSelectedTip } from "../../../../features/tutorials/tutorials-slice";
//TOOLTIP
import { Tooltip } from "react-tippy";
//STYLES
import "./styles.css";
//CUSTOM COMPONENTS
import LevelDisplay from "../../../../components/LevelDisplay";
import ProgressBar from "../../../../components/Progressbar";
import GameButton from "../../../../components/GameButton";
import IconButton from "../../../../components/IconButtons/InfoButton";
/* IMAGES */
import Scribe from "../../../../assets/images/scribe.png";
import { GiConsoleController } from "react-icons/gi";

//
const SidebarHeader = () => {
  const dispatch = useAppDispatch();
  /* REDUX STATE */
  /* REDUX ACTIONS */
  const openDrawer = () => {
    dispatch(updateShowDrawer(true));
  };
  //PLAYER XP STATE
  const xp = useAppSelector((state) => state.xp.value);
  const level = useAppSelector((state) => state.xp.level);
  const xpToNextLevel = useAppSelector((state) => state.xp.xpToNextLevel);
  const progressPercent = useAppSelector((state) => state.xp.progressPercent);
  //SESSION XP STATE
  const sessionXp = useAppSelector((state) => state.sessionXp.value);
  //GIFTXP STATE
  const giftXp = useAppSelector((state) => state.giftXp.value);
  /* ----LOCAL STATE---- */

  return (
    <>
      <div className="flex flex-row justify-start items-center w-full">
        <div className="flex flex-row justify-start items-center w-3/4 pt-2 pl-2">
          <img
            className="__scribe-avatar__  inline-block h-14 w-14 rounded-full mr-2"
            src={Scribe}
            onClick={openDrawer}
          />
          <div className="w-full">
            <p style={{ color: "white" }}> {`You are level ${level}`} </p>
            <Tooltip
              title={`Earn ${xpToNextLevel} XP til level ${level + 1}`}
              position="top"
            >
              <ProgressBar progressPercent={progressPercent} />
            </Tooltip>
          </div>
        </div>
        <div className="w-1/4 flex flex-row justify-around">
          <div className="flex flex-row justify-center items-center">
            <IconButton />
          </div>
        </div>
      </div>
    </>
  );
};

export default SidebarHeader;
