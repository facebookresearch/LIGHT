/* REACT */
import React, { useState } from "react";
/* ICONS */
import { FaStar } from "react-icons/fa";
/* TOOLTIP */
import { Tooltip } from "react-tippy";

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
