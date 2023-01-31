/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../../features/tutorials/tutorials-slice";
/* ---- REDUCER ACTIONS ---- */
import {
  updateChatText,
  updateIsSaying,
  updateTellTarget,
  updateSubmittedMessages,
} from "../../../../../../features/chatInput/chatinput-slice";
/* STYLES */
import "../styles.css";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../components/TutorialPopover";

import { getActionThemeColor } from "../../../../../../app/theme";

import { BiChevronRight } from "react-icons/bi";
import { FaSort } from "react-icons/fa";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatButtons = ({
  onSubmit,
  scrollToBottom,
  resetIdleTimer,
  chatInputRef,
}) => {
  /* ------ REDUX STATE ------ */
  // VIEW STATE
  const isMobile = useAppSelector((state) => state.view.isMobile);
  //   // CHAT STATE
  const chatText = useAppSelector((state) => state.chatInput.chatText);
  const isSaying = useAppSelector((state) => state.chatInput.isSaying);
  const tellTarget = useAppSelector((state) => state.chatInput.tellTarget);
  //   const submittedMessages = useAppSelector(
  //     (state) => state.chatInput.submittedMessages
  //   );
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  //   /* ----REDUX ACTIONS---- */
  //   // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    if (inHelpMode) {
      dispatch(updateSelectedTip(tipNumber));
    }
  };

  /*---------------HANDLERS----------------*/
  const toggleIsSaying = () => {
    console.log("TOGGLE BEING CLICKED");
    if (tellTarget) {
      dispatch(updateTellTarget(""));
      dispatch(updateIsSaying(true));
    } else {
      let toggledValue = !isSaying;
      dispatch(updateIsSaying(toggledValue));
    }
    chatInputRef.current.focus();
  };

  /*---------------HELPERS----------------*/
  const formatTellTargetForButton = (str) => {
    let formattedTellTargetName = str;
    if (str.length > 12) {
      formattedTellTargetName = ` ${formattedTellTargetName.slice(0, 12)}...`;
      if (isMobile) {
        formattedTellTargetName = ` ${formattedTellTargetName.slice(0, 4)}...`;
      }
    }
    return formattedTellTargetName;
  };

  const action = tellTarget ? "tell" : isSaying ? "say" : "do";

  return (
    <div className="_chat-button_ h-full">
      <TutorialPopover
        tipNumber={5}
        open={inHelpMode && selectedTip === 5}
        position="right"
      >
        <button
          onClick={(e) => {
            e.preventDefault();
            if (inHelpMode) {
              setSelectedTip(5);
            } else {
              toggleIsSaying();
            }
          }}
          type="button"
          className={`h-full text-md font-medium rounded shadow-sm text-white pl-2 pr-2 ${getActionThemeColor(
            "bg",
            action
          )} `}
        >
          <span className="flex flex-row  items-center  text-accent-content capitalize">
            {tellTarget ? <BiChevronRight /> : <FaSort />}
            <div className="capitalize w-1/5 overflow-ellipsis pl-1">{`${action} ${
              tellTarget ? formatTellTargetForButton(tellTarget) : ""
            }`}</div>
          </span>
        </button>
      </TutorialPopover>
    </div>
  );
};

export default ChatButtons;

{
  /* <div className="relative ">
<button
  type="button"
  className=" w-40 absolute items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
>
  SAY
</button>
<button
  type="button"
  className=" w-40 absolute  items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-orange-600 my-3 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
>
  DO
</button>
</div> */
}
