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
const PlayerMessage = ({ isSelected, text, caller, actor, xp, onClickFunction }) => {
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

  /*---------------HANDLERS----------------*/
  const clickHandler = ()=>{
    onClickFunction()
  }
  return (
    <div
      className={`_player-message-row_  flex w-full mb-4
      ${inHelpMode && isSelected ? "active" : ""}`}
      onClick={clickHandler}
    >

      <div className="_player-message-container_ flex flex-col w-full">
        <TutorialPopover
          tipNumber={17}
          open={isSelected && inHelpMode && selectedTip === 17}
          position="top"
        >
          <div className="w-full flex flex-row justify-end items-center">
          <div className="w-full flex justify-end items-end">
            {xp ? (
                    <Tooltip
                      title={
                        xp > 0 ? `${xp} Experience Points Earned For Roleplaying` : null
                      }
                    >
                      <AwardStar 
                        xp={xp}
                      />
                    </Tooltip>
                ) : null
                }

              </div>
          <div className="_chatbubble-container_ max-w-[80%]">
          <ChatBubble action={action} actor="YOU" align="right">
            <div className="w-full flex flex-row justify-between items-between ">
            <div className="flex flex-col w-[100%]">
              <p className={`_player-message-bubble-text_ w-full min-w-[50px]  break-words text-left text-md ${action!=="default" ? "text-white" : "text-black"}`}>{text+" "}</p>
            </div>
              <div className="relative">
                <div className="absolute bg-emerald-500"></div>
            </div>
            </div>
          </ChatBubble>
          </div>
          </div>
        </TutorialPopover>
      </div>
    </div>
  );
};
export default PlayerMessage;
