/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppSelector } from "../../../../../app/hooks";
/* STYLES */
import "./styles.css";
/* ICONS */
import { GiHolyGrail } from "react-icons/gi";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

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
    <div className="quest-container">
      <div className="quest-grail__container">
        <TutorialPopover
          tipNumber={13}
          open={inHelpMode && selectedTip === 13}
          position="top"
        >
          <GiHolyGrail className="quest-grail" color="yellow" size="19em" />
          <div
            className={`quest-content ${inHelpMode ? "active" : ""}`}
            onClick={onClickFunction}
          >
            {questInfoArr.map((info, index) => {
              if (info.indexOf(":") >= 0) {
                let traitArr = info.split(":");
                let traitTitle = traitArr[0].toUpperCase();
                let traitDesc = traitArr[1];
                return (
                  <p
                    key={index}
                    className="quest-content__entry"
                    style={{ marginTop: "1px" }}
                  >
                    <span style={{ fontweight: "bold" }}>
                      {traitTitle + ":"}{" "}
                    </span>
                    {traitDesc}
                  </p>
                );
              } else {
                return (
                  <p
                    key={index}
                    className="quest-content__entry"
                    style={{ marginTop: "1px" }}
                  >
                    {info}
                  </p>
                );
              }
            })}
          </div>
        </TutorialPopover>
      </div>
    </div>
  );
};
export default QuestMessage;
