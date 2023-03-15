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
/* ICONS */
import { ImQuotesLeft } from "react-icons/im";
import { ImQuotesRight } from "react-icons/im";
import { RiSingleQuotesL } from "react-icons/ri";

//PlayerMessage - Renders message sent by player to chat with custom styling and displays any xp awarded to message
const PlayerMessage = ({ isSelected, text, caller, actor, xp, onClickFunction }) => {
  //TUTORIAL
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----LOCAL STATE---- */
  const [formattedMessage, setFormattedMessage] = useState("");
  const [tellTarget, setTellTarget] = useState(null)
  const [messageXp, setMessageXp] = useState(0)

  const [action, setAction] = useState("");
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    let formattedText = text;
    let updatedMessageXp = xp;
    let formattedTellTarget = tellTarget;
    let textEndIndex = text.length - 1;
    let firstTextCharacter = text[0];
    let lastTextCharacter = text[textEndIndex];
    let firstFourTextCharacters = text.slice(0, 4);
    console.log("FIRST 4:", firstFourTextCharacters);
    if (firstTextCharacter === '"' && lastTextCharacter === '"') {
      setAction("say");
      formattedText = text.slice(1,text.length-1)
      if(updatedMessageXp >= 2){
        updatedMessageXp = updatedMessageXp-1;
      }else {
        updatedMessageXp =1;
      }
    } else if (firstFourTextCharacters === "tell") {
      setAction("tell");
      let quoteIndex = text.indexOf('"')
      formattedTellTarget = text.slice(5, quoteIndex-1)
      formattedText = text.slice(quoteIndex+1, text.length-1)
    } else {
      setAction("do");
    }
    setFormattedMessage(formattedText);
    setMessageXp(updatedMessageXp)
    setTellTarget(formattedTellTarget);
  }, [text, xp]);

  /*---------------HANDLERS----------------*/
  const clickHandler = ()=>{
    onClickFunction()
  }
  return (
    <div
      className={`_player-message-row_  flex w-full h-full mb-4
      ${inHelpMode && isSelected ? "active" : ""}`}
      onClick={clickHandler}
    >

      <div className="_player-message-container_ flex flex-col w-full">
        <TutorialPopover
          tipNumber={17}
          open={isSelected && inHelpMode && selectedTip === 17}
          position="top"
        >
          <div className="w-full h-full flex flex-row justify-end items-center">
          <div className="w-full h-full flex flex-row justify-end items-center">
            {messageXp > 1 ? (
                    <Tooltip
                      title={
                        messageXp > 1 ? `${messageXp} Experience Points Earned For Roleplaying` : null
                      }
                    >
                      <AwardStar 
                        xp={messageXp}
                      />
                    </Tooltip>
                ) : null
                }
                {
                  action === "say" || action === "tell" ?
                <div className="_quote-container_ relative w-[1px] h-full">
                  <RiSingleQuotesL size={38} className={`_quote-icon-stroke_ absolute ${action === "tell" ? "text-info": "text-accent"} -left-[18px] -top-[18px] z-38`} />
                  <RiSingleQuotesL size={30} className={`_quote-icon_ absolute text-white -left-[14px] -top-[14px] z-40`} />
                  <RiSingleQuotesL size={38} className={`_quote-icon-stroke_ absolute ${action === "tell" ? "text-info": "text-accent"} -left-[8px] -top-[18px] z-38`} />
                  <RiSingleQuotesL size={30} className={`_quote-icon_ absolute text-white -left-[4px] -top-[14px] z-40`} />
                </div>
                :
                null
                }
              </div>
            <div className="_chatbubble-container_ max-w-[80%]">
              <ChatBubble action={action} actor="YOU" align="right">
                <div className="w-full flex flex-row justify-between items-between ">
                 <div className="flex flex-col w-[100%]">
                  <p className={`_player-message-bubble-text_ w-full min-w-[50px]  break-words text-left text-md ${formattedMessage.length < 10 ? "text-center" : "text-right"} ${action!=="default" ? "text-white" : "text-black"}`}>{formattedMessage}</p>
                  {tellTarget?
                  <p className="text-left text-white font-bold italic opacity-50 truncate text-xs mt-1" >Told to {" " + tellTarget}</p>
                  :null
                  }
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
