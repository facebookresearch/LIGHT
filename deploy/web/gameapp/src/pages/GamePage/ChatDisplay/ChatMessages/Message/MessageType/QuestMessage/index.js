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
import { GiHolyGrail } from "react-icons/gi";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../../components/TutorialPopover";

//QuestMessage - Renders message displaying current persona, tracked mission objectives, and any other quests.
const QuestMessage = ({ text, onClickFunction }) => {
  /* ---- REDUX STATE ---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ---- LOCAL STATE---- */
  const [questInfoArr, setQuestInfoArr] = useState([]);
  /* ---- LIFECYCLE STATE---- */
  useEffect(() => {
    let infoArr = text.split("\n");
    setQuestInfoArr(infoArr);
  }, [text]);

  return (
    <div className=" w-full flex justify-center items-center mb-4">
      <TutorialPopover
        tipNumber={13}
        open={inHelpMode && selectedTip === 13}
        position="top"
      >
        <div
          className={`_quest-container_ ${
            inHelpMode ? "active" : ""
          } border-double border-4 rounded border-yellow-100 flex justify-center items-center p-4 `}
        >
          <div
            className={`_quest-content_ prose font-mono text-yellow-100 text-center text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl  2xl:text-2xl`}
            onClick={onClickFunction}
          >
            {questInfoArr.map((info, index) => {
              if (info.indexOf(":") >= 0) {
                let traitArr = info.split(":");
                let traitTitle = traitArr[0].toUpperCase();
                let traitDesc = traitArr[1];
                return (
                  <p key={index} className="_quest-content-entry_">
                    <span style={{ fontweight: "bold" }}>
                      {traitTitle + ":"}{" "}
                    </span>
                    {traitDesc}
                  </p>
                );
              } else {
                return (
                  <p key={index} className="_quest-content-entry_">
                    {info}
                  </p>
                );
              }
            })}
          </div>
        </div>
      </TutorialPopover>
    </div>
  );
};
export default QuestMessage;
