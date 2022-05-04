/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../features/tutorials/tutorials-slice";
/* ---- REDUCER ACTIONS ---- */
import {
  updateChatText,
  updateIsSaying,
  updateTellTarget,
  updateSubmittedMessages,
} from "../../../../../features/chatInput/chatinput-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatInput = ({ onSubmit, scrollToBottom, resetIdleTimer }) => {
  /* ------ REDUX STATE ------ */
  // VIEW STATE
  const isMobile = useAppSelector((state) => state.view.isMobile);
  // CHAT STATE
  const chatText = useAppSelector((state) => state.chatInput.chatText);
  const isSaying = useAppSelector((state) => state.chatInput.isSaying);
  const tellTarget = useAppSelector((state) => state.chatInput.tellTarget);
  const submittedMessages = useAppSelector(
    (state) => state.chatInput.submittedMessages
  );
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    if (inHelpMode) {
      dispatch(updateSelectedTip(tipNumber));
    }
  };
  /*---------------LOCAL STATE----------------*/
  const [cycleMessagesPosition, setCycleMessagesPosition] = useState(0);
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    setCycleMessagesPosition(submittedMessages.length);
  }, [submittedMessages]);

  /*---------------HANDLERS----------------*/
  const toggleIsSaying = () => {
    if (tellTarget) {
      dispatch(updateTellTarget(""));
      dispatch(updateIsSaying(true));
    } else {
      let toggledValue = !isSaying;
      dispatch(updateIsSaying(toggledValue));
    }
  };
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
        dispatch(updateSubmittedMessages(chatText));
        onSubmit(textSubmission);
        dispatch(updateChatText(""));
        scrollToBottom();
      }
    }
  };

  /*---------------HELPERS----------------*/

  return (
    <>
      <div
        className={`chatbox-button ${
          tellTarget !== "" ? "tell" : isSaying ? "say" : "do"
        } ${inHelpMode ? "active" : ""}`}
        onClick={(e) => {
          e.preventDefault();
          if (inHelpMode) {
            setSelectedTip(5);
          } else {
            toggleIsSaying();
          }
        }}
      >
        {tellTarget !== ""
          ? `TELL ${formatTellTargetForButton(tellTarget)}`
          : isSaying
          ? "SAY"
          : "DO"}
        <TutorialPopover
          tipNumber={5}
          open={inHelpMode && selectedTip === 5}
          position="right"
        ></TutorialPopover>
      </div>
      <div
        className={`chatbox-button ${
          tellTarget !== "" ? "tell" : isSaying ? "say" : "do"
        } ${inHelpMode ? "active" : ""}`}
        onClick={(e) => {
          e.preventDefault();
          if (inHelpMode) {
            setSelectedTip(5);
          } else {
            toggleIsSaying();
          }
        }}
      >
        {tellTarget !== ""
          ? `TELL ${formatTellTargetForButton(tellTarget)}`
          : isSaying
          ? "SAY"
          : "DO"}
        <TutorialPopover
          tipNumber={5}
          open={inHelpMode && selectedTip === 5}
          position="right"
        ></TutorialPopover>
      </div>
      <div
        className={`chatbox-button ${
          tellTarget !== "" ? "tell" : isSaying ? "say" : "do"
        } ${inHelpMode ? "active" : ""}`}
        onClick={(e) => {
          e.preventDefault();
          if (inHelpMode) {
            setSelectedTip(5);
          } else {
            toggleIsSaying();
          }
        }}
      >
        {tellTarget !== ""
          ? `TELL ${formatTellTargetForButton(tellTarget)}`
          : isSaying
          ? "SAY"
          : "DO"}
        <TutorialPopover
          tipNumber={5}
          open={inHelpMode && selectedTip === 5}
          position="right"
        ></TutorialPopover>
      </div>
    </>
  );
};

export default ChatInput;
