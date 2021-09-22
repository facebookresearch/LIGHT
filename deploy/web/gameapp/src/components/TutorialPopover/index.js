/* REACT */
import React, { useState, useEffect } from "react";
/* STYLES */
import "./styles.css";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CUSTOM COMPONENTS */
import TutorialContent from "./TutorialContent";
/* COPY */
import GameCopy from "../../GameCopy";
const { tutorialTips } = GameCopy;

const TutorialPopover = ({
  tipNumber,
  open,
  position,
  xOffset,
  yOffset,
  children,
}) => {
  const currentTip = tutorialTips[tipNumber];

  const { title, description } = currentTip;

  return (
    <Tooltip
      interactive={true}
      html={
        <>
          <TutorialContent tip={currentTip} />
        </>
      }
      open={open}
      position={position}
      arrow={true}
      className="tooltip-container"
      sticky={true}
      theme="dark"
      popperOptions={{
        modifiers: {
          preventOverflow: { enabled: false },
          flip: { enabled: false },
          hide: { enabled: false },
        },
      }}
    >
      {children}
    </Tooltip>
  );
};

export default TutorialPopover;
