import React, { useState, useEffect } from "react";

import { Tooltip } from "react-tippy";

import "./styles.css";

import NumberStar from "../CustomIcons/NumberStar";

const LevelDisplay = ({ level, giftExperience }) => {
  const iconStyle = {
    color: "yellow",
    position: "absolute",
    zIndex: "1",
    height: "2.5em",
    width: "2.5em",
  };
  return (
    <div className="levelDisplay-container">
      <Tooltip title="Player Level" position="top">
        <div className="level-container">
          <h5 className="level-number"> LVL </h5>
          <h5 className="level-number">{level}</h5>
        </div>
      </Tooltip>
      <div>
        <Tooltip title="Gift Experience" position="top">
          <NumberStar
            number={giftExperience}
            iconStyle={iconStyle}
            size="2em"
          />
        </Tooltip>
      </div>
    </div>
  );
};

export default LevelDisplay;
