/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect, useMemo } from "react";
/* CUSTOM COMPONENTS */
import { ChatBubble } from "../../../../../../../components/ChatBubble/index.tsx";

//PlayerMessage - Renders message sent by player to chat with custom styling and displays any xp awarded to message
const PlayerMessage = ({ text, action }) => {
  /* ----LOCAL STATE---- */
  const [formatttedMessage, setFormattedMessage] = useState("");
  /*---------------LIFECYCLE----------------*/

  return (
    <div
      className={"_player-message_ flex flex-row justify-end items-center mb-4"}
    >
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
