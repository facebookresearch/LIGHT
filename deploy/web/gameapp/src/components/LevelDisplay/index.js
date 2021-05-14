import React, { useState, useEffect } from "react";

import { Tooltip } from "react-tippy";

import "./styles.css";

import NumberStar from "../CustomIcons/NumberStar";

const LevelDisplay = ({ level, giftExperience }) => {
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
            iconStyle="number-star"
            size="2em"
          />
        </Tooltip>
      </div>
    </div>
  );
};

export default LevelDisplay;
