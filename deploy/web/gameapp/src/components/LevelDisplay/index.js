//REACT
import React, { useState, useEffect } from "react";
//TOOLTIP
import { Tooltip } from "react-tippy";
//STYLE
import "./styles.css";
//CUSTOM COMPONENTS
import NumberStar from "../CustomIcons/NumberStar";
import NumberCircle from "../CustomIcons/NumberCircle";

const LevelDisplay = ({ level, giftExperience }) => {
  return (
    <div className="leveldisplay-container">
      <div className="level-container">
        <Tooltip title="Player Level" position="top">
          <NumberCircle number={level} />
        </Tooltip>
      </div>
      <div className="gift-container">
        <Tooltip title="Gift Experience" position="top">
          <NumberStar number={giftExperience} />
        </Tooltip>
      </div>
    </div>
  );
};

export default LevelDisplay;

/*
      <Tooltip title="Player Level" position="top">
        <div className="level-container">
          <div className="level-circle"/>
          <p style={{margin:0}} className="level-number"> LVL </p>
          <p style={{margin:0}}  className="level-number">{level}</p>
        </div>
      </Tooltip>
    */
