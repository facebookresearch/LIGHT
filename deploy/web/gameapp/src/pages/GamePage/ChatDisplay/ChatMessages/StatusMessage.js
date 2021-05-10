import React, { useState } from "react";

import { FaHeart, FaStar } from "react-icons/fa";
import { Tooltip } from "react-tippy";

const StatusMessage = ({ text }) => {
  let statusArr = text.split("\n");
  console.log("STATUS ARR", statusArr);
  let expStats = parseInt(statusArr[0].split(":")[1]);
  let rewardStats = parseInt(statusArr[1].split(":")[1]);
  let strengthStats = statusArr[2];
  let sizeStats = statusArr[3];
  let toughnessStats = statusArr[4];
  let dexterityStats = statusArr[45];
  return (
    <div className=" status-container">
      <div className="status-heart__container">
        <FaHeart className="status-heart" color="red" size="20em" />

        <div className="status-content">
          <p className="status-content__entry" style={{ marginTop: "1px" }}>
            EXPERIENCE POINTS: {expStats}
            <span>
              <FaStar color="yellow" />
            </span>
          </p>
          <p className="status-content__entry" style={{ marginTop: "1px" }}>
            REWARDS LEFT TO GIVE: {rewardStats}
            <span>
              <FaStar color="yellow" />
            </span>
          </p>
          <p className="status-content__entry" style={{ marginTop: "1px" }}>
            {strengthStats}
          </p>
          <p className="status-content__entry" style={{ marginTop: "1px" }}>
            {sizeStats}
          </p>
          <p className="status-content__entry" style={{ marginTop: "1px" }}>
            {toughnessStats}
          </p>
          <p className="status-content__entry" style={{ marginTop: "1px" }}>
            {dexterityStats}
          </p>
        </div>
      </div>
    </div>
  );
};
export default StatusMessage;
