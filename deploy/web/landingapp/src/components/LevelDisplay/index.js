/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import NumberStar from "../CustomIcons/NumberStar";
import NumberCircle from "../CustomIcons/NumberCircle";

//LevelDisplay-Renders Level and gift exp on custom icons at the head of the side bar in player info component
const LevelDisplay = () => {
  return (
    <div className="leveldisplay-container">
      <div className="level-container">
        <NumberCircle number={0} />
      </div>
      <div className="gift-container">
        <NumberStar number={0} />
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
