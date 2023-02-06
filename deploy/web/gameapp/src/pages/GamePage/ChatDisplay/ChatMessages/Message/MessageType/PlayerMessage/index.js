/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect, useMemo } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../../components/TutorialPopover";
import { ChatBubble } from "../../../../../../../components/ChatBubble";
import AwardStar from "../../../../../../../components/Stars/AwardStar";

//PlayerMessage - Renders message sent by player to chat with custom styling and displays any xp awarded to message
const PlayerMessage = ({ text, caller, actor, xp, onClickFunction }) => {
  //TUTORIAL
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----LOCAL STATE---- */
  const [formatttedMessage, setFormattedMessage] = useState("");

  const [action, setAction] = useState("");
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    let textEndIndex = text.length - 1;
    let firstTextCharacter = text[0];
    let lastTextCharacter = text[textEndIndex];
    let firstFourTextCharacters = text.slice(0, 4);
    console.log("FIRST 4:", firstFourTextCharacters);
    if (firstTextCharacter === '"' && lastTextCharacter === '"') {
      setAction("say");
    } else if (firstFourTextCharacters === "tell") {
      setAction("tell");
    } else {
      setAction("do");
    }
  }, [text]);

  return (
    <div
      className={`_player-message_  flex w-full mb-4
      ${inHelpMode ? "active" : ""}`}
      onClick={onClickFunction}
    >

      <div className="flex flex-col w-full">
        <TutorialPopover
          tipNumber={17}
          open={inHelpMode && selectedTip === 17}
          position="top"
        >
          <ChatBubble action={action} actor="YOU" align="right">
            <div className="w-full flex flex-row justify-between items-between">
            {xp ? (
                    <Tooltip
                      title={
                        xp > 0 ? `${xp} Experience Points Earned For Roleplaying` : null
                      }
                    >
                      <AwardStar 
                        xp={12}
                      />
                    </Tooltip>
                ) : null
                }
             <div className="w-full flex justify-start items-start">
              </div>
            <div className="flex flex-col w-full">
              <p className="_player-message-bubble-text_ w-full  break-words">{text}</p>
              <div className="relative">
                <div className="absolute bg-emerald-500"></div>
              </div>
            </div>
            </div>
          </ChatBubble>
        </TutorialPopover>
      </div>
    </div>
  );
};
export default PlayerMessage;
