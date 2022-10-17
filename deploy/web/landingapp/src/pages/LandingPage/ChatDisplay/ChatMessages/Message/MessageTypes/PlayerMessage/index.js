/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect, useMemo } from "react";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CUSTOM COMPONENTS */
import { ChatBubble } from "../../../../../../../components/ChatBubble/index.tsx";

//PlayerMessage - Renders message sent by player to chat with custom styling and displays any xp awarded to message
const PlayerMessage = ({ text, caller, actor, xp, onClickFunction }) => {
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
      {xp ? (
        <>
          <span id="message-star__container">
            <p id="message-star__number">{xp}</p>
            <i id="message-star" className="fa fa-star" />
          </span>
        </>
      ) : null}
      <div className="ml-10">
        <ChatBubble action={action} actor="YOU" align="right">
          <div className="max-w-md break-words">{text}</div>
          <div className="relative">
            <div className="absolute bg-emerald-500"></div>
          </div>
        </ChatBubble>
      </div>
    </div>
  );
};
export default PlayerMessage;
