/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect, useMemo } from "react";
/* STYLING */
import { getActionThemeColor } from "../../app/theme";

//Checks alignment, actor name, and action type.
interface Props {
  align: "left" | "right";
  action: string;
  actor: string;
  children: React.ReactNode;
}

//ChatBubbleTail - orients chat bubble tail to correct side.
function ChatBubbleTail({
  align,
  action,
}: {
  align: "left" | "right";
  action: string;
}) {
  const polygon =
    align === "left" ? "100 0, 100 100, 20 50" : "0 0, 0 100, 80 50";

  return (
    <div className={`w-3 h-3 ${align === "left" ? "ml-2" : "mr-2"}`}>
      <svg id="triangle" viewBox="0 0 100 100">
        <polygon
          points={polygon}
          className={getActionThemeColor("fill", action)}
        />
      </svg>
    </div>
  );
}

//CharacterName - Character name plate
function CharacterName({ name }: { name: string }) {
  return (
    <div className="text-sm font-semibold text-base-100 whitespace-pre">
      {name}
    </div>
  );
}

//ChatBubble - Chat bubble that agent and user messages appear in.  User message to the right agent messages to the left.  Color of messages is determined by action
export function ChatBubble({
  align = "left",
  action = "default",
  actor,
  children,
}: Props) {
  return (
    <div className="flex flex-row items-center">
      {align === "left" && <CharacterName name={actor} />}
      {align === "left" && <ChatBubbleTail align={align} action={action} />}
      <div
        className={`_chat_bubble_ relative p-4 min-h-[50px] font-medium
        ${getActionThemeColor("bg", action)} ${getActionThemeColor(
          "text",
          action
        )}
        rounded-md flex justify-center items-center`}
      >
        <div>{children}</div>
      </div>
      {align === "right" && <ChatBubbleTail align={align} action={action} />}
      {align === "right" && <CharacterName name={actor} />}
    </div>
  );
}
