/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect, useMemo } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

import { ChatBubble } from "../../../../../components/ChatBubble";

//PlayerMessage - Renders message sent by player to chat with custom styling and displays any xp awarded to message
const PlayerMessage = ({ text, caller, actor, xp, onClickFunction }) => {
  // let classNames = "message type-dialogue ";
  // if (["tell", "say", "whisper"].includes(caller)) {
  //   text = "&ldquo;" + text + "&rdquo;";
  //   classNames = "message type-dialogue ";
  // }
  // classNames += "me";

  /* ----REDUX STATE---- */
  console.log("CALLER:  ", caller);
  console.log("ACTOR:  ", actor);
  console.log("MESSAGE TEXT:", text);
  console.log("XP", xp);

  //TUTORIAL;
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
      className={`_player-message_ flex flex-row justify-end items-center mb-4
      ${inHelpMode ? "active" : ""}`}
      onClick={onClickFunction}
    >
      <div className="ml-10">
        <ChatBubble action={action} actor="YOU" align="right">
          <div className="max-w-md break-words">
            {text}
          </div>
          <div className="relative">
            <div className="absolute bg-emerald-500">
              <TutorialPopover
                tipNumber={17}
                open={inHelpMode && selectedTip === 17}
                position="top"
              ></TutorialPopover>
            </div>
          </div>
        </ChatBubble>
      </div>
      {xp ? (
        <>
          <Tooltip
            title={
              xp > 0 ? `${xp} Experience Points Earned For Roleplaying` : null
            }
          >
            <span id="message-star__container">
              <p id="message-star__number">{xp}</p>
              <i id="message-star" className="fa fa-star" />
            </span>
          </Tooltip>
        </>
      ) : null}
    </div>
  );
};
export default PlayerMessage;
