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
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../components/TutorialPopover";

//ICONS
import { MdOutlineArrowForwardIos } from "react-icons/md";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const SendButton = ({ onSubmit, scrollToBottom, resetIdleTimer }) => {
  /* ------ REDUX STATE ------ */
  // VIEW STATE
  const isMobile = useAppSelector((state) => state.view.isMobile);
  //   // CHAT STATE
  const chatText = useAppSelector((state) => state.chatInput.chatText);
  const isSaying = useAppSelector((state) => state.chatInput.isSaying);
  const tellTarget = useAppSelector((state) => state.chatInput.tellTarget);
  const submittedMessages = useAppSelector(
    (state) => state.chatInput.submittedMessages
  );
  //   //TUTORIAL;
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
  //   /*---------------LOCAL STATE----------------*/
  //   const [cycleMessagesPosition, setCycleMessagesPosition] = useState(0);
  //   /*---------------LIFECYCLE----------------*/
  //   useEffect(() => {
  //     setCycleMessagesPosition(submittedMessages.length);
  //   }, [submittedMessages]);

  /*---------------HANDLERS----------------*/
  const chatSubmissionHandler = (e) => {
    e.preventDefault();

    if (!inHelpMode) {
      let textSubmission;
      if (!!chatText) {
        if (tellTarget !== "") {
          textSubmission = `tell ${tellTarget} "${chatText}"`;
        } else if (isSaying) {
          textSubmission = `"${chatText}"`;
        } else {
          textSubmission = chatText;
        }
        resetIdleTimer();
        dispatch(updateSubmittedMessages(chatText));
        onSubmit(textSubmission);
        dispatch(updateChatText(""));
        scrollToBottom();
      }
    }
  };

  const toggleIsSaying = () => {
    if (tellTarget) {
      dispatch(updateTellTarget(""));
      dispatch(updateIsSaying(true));
    } else {
      let toggledValue = !isSaying;
      dispatch(updateIsSaying(toggledValue));
    }
  };

  /*---------------HELPERS----------------*/

  /* ----------TAILWIND CLASSES--------- */
  const classNames = {};
  return (
    <>
      <TutorialPopover
        tipNumber={7}
        open={inHelpMode && selectedTip === 7}
        position="left"
      >
        <MdOutlineArrowForwardIos
          onClick={inHelpMode ? () => setSelectedTip(7) : chatSubmissionHandler}
          className="text-2xl font-bold text-green-200 hover:text-red-100"
        />
      </TutorialPopover>
    </>
  );
};

export default SendButton;
