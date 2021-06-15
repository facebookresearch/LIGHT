import React, { useState, useEffect } from "react";

import { Tooltip } from "react-tippy";

import "./styles.css";

import NumberStar from "../CustomIcons/NumberStar";

const LevelDisplay = ({ level, giftExperience }) => {
  return (
    <div className="levelDisplay-container">
      <Tooltip title="Player Level" position="top">
        <div className="level-container">
          <p className="level-number"> LVL </p>
          <p className="level-number">{level}</p>
        </div>
      </Tooltip>
      <div>
        <Tooltip title="Gift Experience" position="top">
          <NumberStar number={giftExperience} iconStyle="number-star" />
        </Tooltip>
      </div>
    </div>
  );
};

export default LevelDisplay;
