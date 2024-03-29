/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
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
      style={{ animation: "none" }}
      theme="dark"
      size="small"
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
