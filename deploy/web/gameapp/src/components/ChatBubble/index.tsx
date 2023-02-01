import React, { useState, useEffect, useMemo } from "react";

import { getActionThemeColor } from "../../app/theme";

interface Props {
  align: "left" | "right";
  action: string;
  actor: string;
  children: React.ReactNode;
}

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

function CharacterName({
  align,
  name,
}: {
  name: string;
  align: "left" | "right";
}) {
  return (
    <div
      className={`text-sm font-semibold break-words ${
        align === "left" ? "text-black" : "text-white"
      } sm:$${
        align === "left" ? "text-black" : "text-white"
      } md:text-white lg:text-white xl:text-white 2xl:text-white whitespace-pre`}
    >
      {name}
    </div>
  );
}

export function ChatBubble({
  align = "left",
  action = "default",
  actor,
  children,
}: Props) {
  return (
    <div className="w-full">
      <div
        className={`${
          align === "left" ? "justify-start" : "justify-end"
        } hidden sm:hidden md:flex lg:flex xl:flex 2xl:flex flex-row items-center `}
      >
        {align === "left" && <CharacterName name={actor} align={align} />}
        {align === "left" && <ChatBubbleTail align={align} action={action} />}
        <div
          className={`_chat_bubble_ max-w-[80%] min-w-[20%] relative p-4 min-h-[50px] font-medium
        ${getActionThemeColor("bg", action)} ${getActionThemeColor(
            "text",
            action
          )}
        rounded-md flex justify-center items-center`}
        >
          <div className="max-w-[100%]">{children}</div>
        </div>
        {align === "right" && <ChatBubbleTail align={align} action={action} />}
        {align === "right" && <CharacterName name={actor} align={align} />}
      </div>
      <div
        className={`w-full flex flex-row items-center ${
          align === "left" ? "justify-start" : "justify-end"
        } sm:flex md:hidden lg:hidden xl:hidden 2xl:hidden`}
      >
        <div
          className={`_chat_bubble_ max-w-[80%] min-w-[40%] flex justify-center items-center p-4 min-h-[50px] font-medium
        ${getActionThemeColor("bg", action)} ${getActionThemeColor(
            "text",
            action
          )}
        rounded-md`}
        >
          <div className="max-w-[80%]">
            <div
              className={`w-full flex flex-row ${
                align === "left" ? "justify-start" : "justify-end"
              }`}
            >
              <CharacterName name={actor} align={align} />
            </div>
            <div className="max-w-[100%] min-w-[40%]">{children}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
