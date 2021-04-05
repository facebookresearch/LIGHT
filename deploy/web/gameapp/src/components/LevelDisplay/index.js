import React, { useState, useEffect } from "react";

import "./styles.css";

import NumberStar from "../CustomIcons/NumberStar";

const LevelDisplay = (props) => {
  const { level, giftExp } = props;
  const iconStyle = {
    color: "yellow",
    position: "absolute",
    zIndex: "-1",
  };
  return (
    <div className="levelDisplay-container">
      <div className="level-container">
        <h1 className="level-number"> LVL </h1>
        <h1 className="level-number">{level}</h1>
      </div>
      <NumberStar number={giftExp} iconStyle={iconStyle} />
    </div>
  );
};

export default LevelDisplay;
