/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
/* THEME */
import { getActionThemeColor } from "../../app/theme";

interface Props {
  align: "left" | "right";
  action: string;
  actor: string;
  mobile: boolean;
  children: React.ReactNode;
}

// ChatBubbleTail - Renders chat bubble tail aligned properly
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
    <div
      className={`_chat-tail-container_ w-3 h-3 ${
        align === "left" ? "ml-2" : "mr-2"
      }`}
    >
      <svg id="triangle" viewBox="0 0 100 100">
        <polygon
          points={polygon}
          className={getActionThemeColor("fill", action)}
        />
      </svg>
    </div>
  );
}

// CharacterName - Renders character name plate styled and oriented based on source
function CharacterName({
  action,
  align,
  name,
  mobile,
}: {
  action: string;
  mobile: boolean;
  name: string;
  align: "left" | "right";
}) {
  return (
    <div
      className={`_nameplate-container_ flex ${
        align === "left" ? "justify-start" : "justify-end"
      }`}
    >
      <p
        className={`_nameplate-text_ max-w-[100px] text-md font-semibold break-words truncate ${
          !mobile || action === "say" || action === "do"
            ? "text-white"
            : "text-black"
        }`}
      >
        {name}
      </p>
    </div>
  );
}

// ChatBubble - renders chatbubble component with children prop as bubble content
export function ChatBubble({
  align = "left",
  action = "default",
  actor,
  children,
}: Props) {
  return (
    <>
      <div
        className={`_chatbubble-container_ ${
          align === "left" ? "justify-start" : "justify-end"
        } hidden sm:hidden md:flex lg:flex xl:flex 2xl:flex flex-row items-center `}
      >
        {align === "left" && (
          <CharacterName
            name={actor}
            align={align}
            action={action}
            mobile={false}
          />
        )}
        {align === "left" && <ChatBubbleTail align={align} action={action} />}
        <div
          className={`_chat_bubble_ w-full min-w-[10%] flex relative p-4 min-h-[50px] font-medium overflow-hidden
        ${getActionThemeColor("bg", action)} ${getActionThemeColor(
            "text",
            action
          )}
        rounded-md flex flex-row justify-center items-center`}
        >
          <div className="_chatbubble-body_ w-full ">{children}</div>
        </div>
        {align === "right" && <ChatBubbleTail align={align} action={action} />}
        {align === "right" && (
          <CharacterName
            name={actor}
            align={align}
            action={action}
            mobile={false}
          />
        )}
      </div>
      <div
        className={`_mobile-chatbubble-row_ flex flex-row items-center ${
          align === "left" ? "justify-start" : "justify-end"
        } sm:flex md:hidden lg:hidden xl:hidden 2xl:hidden`}
      >
        <div
          className={`_mobile-chatbubble-container_ w-full overflow-hidden flex justify-center items-center p-4 min-h-[50px] font-medium
        ${getActionThemeColor("bg", action)} ${getActionThemeColor(
            "text",
            action
          )}
        rounded-md`}
        >
          <div className="_mobile-chatbubble-body_ w-full">
            <div
              className={`_mobile-chatbubble-nameplate-container_ w-full flex${
                align === "left" ? "justify-start" : "justify-end"
              }`}
            >
              <CharacterName
                name={actor}
                align={align}
                action={action}
                mobile={true}
              />
            </div>
            <div
              className={`_mobile-chatbubble-body_ w-full ${
                align === "left" ? "text-left" : "text-right"
              }`}
            >
              {children}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
