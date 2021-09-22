/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppSelector } from "../../../../../app/hooks";
/* STYLES */
import "./styles.css";
/* ICONS */
import { FaHeart, FaStar } from "react-icons/fa";

//StatusMessage - Renders Status Message detailing players stats and experience.
const StatusMessage = ({ text, onClickFunction }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----LOCAL STATE ---- */
  const [statusArr, setStatusArr] = useState([]);
  /* ---- LIFECYCLE ---- */
  useEffect(() => {
    let statusArr = text.split("\n");
    setStatusArr(statusArr);
  }, [text]);

  return (
    <div
      className={`status-container ${inHelpMode ? "active" : ""}`}
      onClick={onClickFunction}
    >
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
                  EXPERIENCE {index == 1 ? "GIFT " : ""}POINTS: {starStat}
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
