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
    <TutorialPopover
    tipNumber={13}
    open={inHelpMode && selectedTip === 13}
    position="top"
  >
    <div className="_message-row_ w-full flex justify-center items-center mb-4">
        <div
          className={`_quest-container_ ${
            inHelpMode ? "active" : ""
          } w-5/6 md:w-2/3 flex border-solid border-4 rounded border-white justify-center items-center p-4 `}
        >
          <div
            className={`_quest-content_ prose text-white text-center text-md`}
            onClick={onClickFunction}
          >
            <div className="_quest-content-header_ w-full flex flex-row justify-center items-center ">
              <p className="_quest-content-header-text_ font-bold">MISSIONS</p>
              <GiHolyGrail className="_quest-content-header-icon_ text-4xl text-white  ml-2"/>
            </div>
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
    </div>
  </TutorialPopover>
  );
};
export default QuestMessage;
