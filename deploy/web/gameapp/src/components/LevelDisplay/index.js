/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CUSTOM COMPONENTS */
import NumberStar from "../CustomIcons/NumberStar";
import NumberCircle from "../CustomIcons/NumberCircle";

//LevelDisplay-Renders Level and gift exp on custom icons at the head of the side bar in player info component
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
