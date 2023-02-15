/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useState, useEffect} from "react";
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
  //HELP MODE
  const toggleHelpMode = () => {
    let helpModeUpdate = !inHelpMode;
    let isClickedUpdate = !isClicked
    dispatch(updateInHelpMode(helpModeUpdate));
    setIsClicked(isClickedUpdate)
  };
  /* ----LOCAL STATE---- */
  const [isClicked, setIsClicked] = useState(false)
  /* ----LIFECYCLE---- */
  useEffect(()=>{
    if(isClicked){
      setIsClicked(false);
    }
  }, [selectedTip])
  return (
      <TutorialPopover
        tipNumber={0}
        open={isClicked && inHelpMode && selectedTip === 0}
        position="bottom"
      >
            <Tooltip title="HELP MODE" position="top">
        <BsInfo
          className={`iconbutton-icon ${inHelpMode ? "active" : ""} `}
          onClick={toggleHelpMode}
        />
            </Tooltip>
      </TutorialPopover>
  );
};

export default IconButton;
