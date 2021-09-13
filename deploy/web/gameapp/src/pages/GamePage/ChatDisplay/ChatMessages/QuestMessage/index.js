/* REACT */
import React, { useState, useEffect } from "react";
/* ICONS */
import { GiHolyGrail } from "react-icons/gi";
/* TOOLTIP */
import { Tooltip } from "react-tippy";

const QuestMessage = ({ text }) => {
  const [questInfoArr, setQuestInfoArr] = useState([]);
  useEffect(() => {
    let infoArr = text.split("\n");
    setQuestInfoArr(infoArr);
  }, [text]);

  return (
    <div className="quest-container">
      <div className="quest-grail__container">
        <GiHolyGrail className="quest-grail" color="yellow" size="19em" />
        <div className="quest-content">
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
      </div>
    </div>
  );
};
export default QuestMessage;
