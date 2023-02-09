/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppSelector } from "../../../../../../../app/hooks";
/* STYLES */
import "./styles.css";
/* ICONS */
import { FaHeart, FaStar } from "react-icons/fa";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../../components/TutorialPopover";

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
    <div className="w-full flex justify-center items-center mb-10">
      <div
        className={`_status-container_ w-4/5 overflow-hidden border-4 rounded border-red-400 border-double flex justify-center items-center p-4 ${
          inHelpMode ? "active" : ""
        }`}
        onClick={onClickFunction}
      >
        <div
          className={`_status-content_ text-white text-md`}
        >
          <TutorialPopover
            tipNumber={12}
            open={inHelpMode && selectedTip === 12}
            position="top"
          >
            {statusArr.map((stat, index) => {
              if (index <= 1) {
                let starStat = parseInt(stat.split(":")[1]);
                return (
                  <p className="_status-content__entry_ flex flex-row justify-center items-center ">
                    XP {index == 1 ? "GIFT " : ""}POINTS:
                    <span className="_star-count_ flex flex-row justify-center items-center">
                      {starStat}
                      <FaStar color="yellow" />
                    </span>
                  </p>
                );
              } else {
                return (
                  <p className="_status-content__entry_ text-white">{stat}</p>
                );
              }
            })}
          </TutorialPopover>
        </div>
      </div>
    </div>
  );
};
export default StatusMessage;
