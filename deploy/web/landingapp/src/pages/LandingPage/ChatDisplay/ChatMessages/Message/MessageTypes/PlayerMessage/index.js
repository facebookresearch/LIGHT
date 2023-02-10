/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* CUSTOM COMPONENTS */
import { ChatBubble } from "../../../../../../../components/ChatBubble/index.tsx";

//PlayerMessage - Renders message sent by player to chat with custom styling and displays any xp awarded to message
const PlayerMessage = ({ text, action }) => {
  return (
    <div
      className={`_player-message-row_  flex w-full mb-4`}
    >
      <div className="_player-message-container_ flex flex-col w-full">
          <div className="w-full flex flex-row justify-end items-center">
          <div className="_chatbubble-container_ max-w-[80%]">
          <ChatBubble action={action} actor="YOU" align="right">
            <div className="w-full flex flex-row justify-between items-between ">
            <div className="flex flex-col w-[90%]">
              <p className={`_player-message-bubble-text_ w-full min-w-[40px]  break-words text-left text-md ${action!=="default" ? "text-white" : "text-black"}`}>{text}</p>
            </div>
              <div className="relative">
                <div className="absolute bg-emerald-500"></div>
            </div>
            </div>
          </ChatBubble>
          </div>
          </div>
      </div>
    </div>
  );
};
export default PlayerMessage;
