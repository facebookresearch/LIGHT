/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* ICONS */
import { FaStar } from "react-icons/fa";

const MissionCompleteMessage = ({ xp, name }) => {
  return (
    <div className=" missionsuccess-container">
      <div className="missionsuccess-star__container">
        <p id="missionsuccess-header">MISSION SUCCESS!</p>
        <FaStar className="missionsuccess-star" color="yellow" size="10em" />
        <h1 className="missionsuccess-star__exp">{xp}XP</h1>
        <div className="missionsuccess-banner">
          <p
            className="missionsuccess-banner__text"
            style={{ textDecoration: "underline", margin: "0px" }}
          >
            COMPLETED
          </p>
          <p
            className="missionsuccess-banner__text"
            style={{ marginTop: "1px" }}
          >
            {name}
          </p>
        </div>
      </div>
    </div>
  );
};
export default MissionCompleteMessage;
