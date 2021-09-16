/* REACT */
import React, { useState, useEffect } from "react";
/* STYLES */
import "./styles.css";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* COPY */
import GameCopy from "../../GameCopy";
const { tutorialTips } = GameCopy;

const TutorialPopover = ({ tipNumber, open, position, children }) => {
  const currentTip = tutorialTips[tipNumber];

  const { title, description } = currentTip;

  return (
    <Tooltip
      style={{ all: "initial" }}
      html={
        <>
          <h5>{title}</h5>
          <p>{description}</p>
        </>
      }
      open={open}
      position={position}
      arrow={true}
    >
      {children}
    </Tooltip>
  );
};

export default TutorialPopover;
