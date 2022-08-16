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
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../components/TutorialPopover";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatInput = ({ onSubmit, scrollToBottom, resetIdleTimer }) => {
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

  const toggleIsSaying = () => {
    if (tellTarget) {
      dispatch(updateTellTarget(""));
      dispatch(updateIsSaying(true));
    } else {
      let toggledValue = !isSaying;
      dispatch(updateIsSaying(toggledValue));
    }
  };
  //   /*---------------LOCAL STATE----------------*/
  const [cycleMessagesPosition, setCycleMessagesPosition] = useState(0);
  //   /*---------------LIFECYCLE----------------*/

  /*---------------HANDLERS----------------*/

  /*---------------HELPERS----------------*/

  /* ----------TAILWIND CLASSES--------- */
  const classNames = {
    chatbarContainer: "flex flex-row w-full border-4 rounded border-green-400",
    chatbar: "flex flex-row",
  };

  return (
    <>
      <input
        autoFocus
        name="chat"
        id="chat"
        autocomplete="off"
        style={{ caretColor: "green" }}
        className={`chatbox-input ${
          inHelpMode ? "active" : ""
        } text-green-100 w-full shadow-sm bg-transparent placeholder-green-100 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border-gray-300 rounded-md`}
        placeholder={`${
          tellTarget ? `Tell ${tellTarget}` : isSaying ? "Say" : "Do"
        } Something`}
        value={chatText}
        onClick={(e) => {
          e.preventDefault();
          if (inHelpMode) {
            setSelectedTip(6);
          }
        }}
        onChange={(e) => {
          resetIdleTimer();
          dispatch(updateChatText(e.target.value));
        }}
        onKeyDown={(e) => {
          if (e.key == "`") {
            e.preventDefault();
            toggleIsSaying();
          }
          if (e.key == "ArrowUp") {
            e.preventDefault();
            if (inHelpMode) {
              console.log(" HELP MODE ARROW UP KEY PRESS");
              let nextTip = selectedTip + 1;
              if (nextTip > 8) {
                nextTip = 0;
              }
              console.log("TIP cylce", nextTip);
              setSelectedTip(nextTip);
            } else {
              if (submittedMessages.length > 0) {
                let updatedPosition = cycleMessagesPosition - 1;
                if (updatedPosition < 0) {
                  updatedPosition = submittedMessages.length;
                }
                setCycleMessagesPosition(updatedPosition);
                dispatch(updateChatText(submittedMessages[updatedPosition]));
              }
            }
          }
          if (e.key == "ArrowDown") {
            e.preventDefault();
            if (inHelpMode) {
              let lastTip = selectedTip - 1;
              if (lastTip < 0) {
                lastTip = 8;
              }
              setSelectedTip(lastTip);
            } else {
              if (submittedMessages.length > 0) {
                let updatedPosition = cycleMessagesPosition + 1;
                if (updatedPosition >= submittedMessages.length) {
                  updatedPosition = 0;
                }
                setCycleMessagesPosition(updatedPosition);
                dispatch(updateChatText(submittedMessages[updatedPosition]));
              }
            }
          }
          if (e.key === "Enter") {
            const prefix = e.target.value.startsWith('"') ? "" : '"';
            const suffix = e.target.value.endsWith('"') ? "" : '"';
            dispatch(updateChatText(`${prefix} ${e.target.value} ${suffix}`));
            onSubmit(e);
          }
        }}
      />
    </>
  );
};

export default ChatInput;
