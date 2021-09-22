/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { updateSelectedTip } from "../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../TutorialPopover";
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
  const setSelectedTip = (tipNumber) => {
    dispatch(updateSelectedTip(tipNumber));
  };
  return (
    <Tooltip title="HELP MODE" position="top">
      <TutorialPopover
        tipNumber={0}
        open={inHelpMode && selectedTip === 0}
        position="right"
      >
        <BsInfo
          className={`iconbutton ${active ? "active" : ""} `}
          onClick={buttonFunction}
        />
      </TutorialPopover>
    </Tooltip>
  );
};

export default IconButton;
