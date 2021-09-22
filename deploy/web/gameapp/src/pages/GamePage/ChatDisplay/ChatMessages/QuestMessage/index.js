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
    <div
      className={`quest-container ${inHelpMode ? "active" : ""}`}
      onClick={onClickFunction}
    >
      <div className="quest-grail__container">
        <GiHolyGrail className="quest-grail" color="yellow" size="19em" />
        <div className="quest-content">
          <TutorialPopover
            tipNumber={13}
            open={inHelpMode && selectedTip === 13}
            position="left"
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
          </TutorialPopover>
        </div>
      </div>
    </div>
  );
};
export default QuestMessage;
