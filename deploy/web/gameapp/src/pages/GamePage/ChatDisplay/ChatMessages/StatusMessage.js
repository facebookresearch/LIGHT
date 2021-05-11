import React, { useState, useEffect } from "react";

import { FaHeart, FaStar } from "react-icons/fa";
import { Tooltip } from "react-tippy";

const StatusMessage = ({ text }) => {
  const [statusArr, setStatusArr] = useState([]);
  useEffect(() => {
    let statusArr = text.split("\n");
    setStatusArr(statusArr);
  }, [text]);

  return (
    <div className=" status-container">
      <div className="status-heart__container">
        <FaHeart className="status-heart" color="red" size="19em" />
        <div className="status-content">
          {statusArr.map((stat, index) => {
            if (index <= 1) {
              let starStat = parseInt(stat.split(":")[1]);
              return (
                <p
                  className="status-content__entry"
                  style={{ marginTop: "1px" }}
                >
                  EXPERIENCE POINTS: {starStat}
                  <span>
                    <FaStar color="yellow" />
                  </span>
                </p>
              );
            } else {
              return (
                <p
                  className="status-content__entry"
                  style={{ marginTop: "1px" }}
                >
                  {stat}
                </p>
              );
            }
          })}
        </div>
      </div>
    </div>
  );
};
export default StatusMessage;
