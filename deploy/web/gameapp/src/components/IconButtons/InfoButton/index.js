/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import {
  updateSelectedTip,
  updateInHelpMode,
} from "../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../TutorialPopover";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* ICONS */
import { BsInfo } from "react-icons/bs";

//IconButton - Renders button that toggles help mode.
const IconButton = ({ buttonFunction, active }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const toggleHelpMode = () => {
    let helpModeUpdate = !inHelpMode;
    dispatch(updateInHelpMode(helpModeUpdate));
  };

  return (
    <Tooltip title="HELP MODE" position="top">
      <TutorialPopover
        tipNumber={0}
        open={inHelpMode && selectedTip === 0}
        position="right"
      >
        <BsInfo
          className={`iconbutton-icon ${inHelpMode ? "active" : ""} `}
          onClick={toggleHelpMode}
        />
      </TutorialPopover>
    </Tooltip>
  );
};

export default IconButton;
