import React, { useState, useEffect } from "react";

import "./styles.css";

import NumberStar from "../CustomIcons/NumberStar";

const LevelDisplay = (props) => {
  const { level, giftExp } = props;
  const iconStyle = {
    color: "yellow",
    position: "absolute",
    zIndex: "-1",
    height: "5em",
    width: "5em",
  };
  return (
    <div className="levelDisplay-container">
      <div className="level-container">
        <h2 className="level-number"> LVL </h2>
        <h2 className="level-number">{level}</h2>
      </div>
      <div style={{ width: "60%" }}>
        <NumberStar number={giftExp} iconStyle={iconStyle} size="4em" />
      </div>
    </div>
  );
};

export default LevelDisplay;
