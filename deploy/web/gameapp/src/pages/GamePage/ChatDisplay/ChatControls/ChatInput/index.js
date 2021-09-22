/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import {
  updateChatText,
  updateIsSaying,
  updateTellTarget,
  updateSubmittedMessages,
} from "../../../../../features/chatInput/chatinput-slice";
/* STYLES */
import "./styles.css";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatInput = ({ onSubmit, scrollToBottom, resetIdleTimer }) => {
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  // CHAT STATE
  const chatText = useAppSelector((state) => state.chatInput.chatText);
  const isSaying = useAppSelector((state) => state.chatInput.isSaying);
  const tellTarget = useAppSelector((state) => state.chatInput.tellTarget);
  const submittedMessages = useAppSelector(
    (state) => state.chatInput.submittedMessages
  );

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
  };

  /*---------------HELPERS----------------*/
  const formatTellTargetForButton = (str) => {
    let formattedTellTargetName = str.toUpperCase();
    if (str.length > 7) {
      formattedTellTargetName = ` ${formattedTellTargetName.slice(0, 7)}...`;
    }
    return formattedTellTargetName;
  };

  return (
    <div className="chatbar-container">
      <form style={{ display: "flex" }} onSubmit={chatSubmissionHandler}>
        <div className="chatbar">
          <div
            className={`chatbox-button ${isSaying ? "say" : "do"}`}
            onClick={(e) => {
              e.preventDefault();
              toggleIsSaying();
            }}
          >
            {tellTarget !== ""
              ? `TELL ${formatTellTargetForButton(tellTarget)}`
              : isSaying
              ? "SAY"
              : "DO"}
          </div>
          <input
            className="chatbox-input"
            value={chatText}
            onChange={(e) => {
              resetIdleTimer();
              dispatch(updateChatText(e.target.value));
            }}
            onKeyDown={(e) => {
              if (e.key == "`") {
                e.preventDefault();
                toggleIsSaying();
              }
              if (submittedMessages.length > 0) {
                if (e.key == "ArrowUp") {
                  e.preventDefault();
                  let updatedPosition = cycleMessagesPosition - 1;
                  if (updatedPosition < 0) {
                    updatedPosition = submittedMessages.length;
                  }
                  setCycleMessagesPosition(updatedPosition);
                  dispatch(updateChatText(submittedMessages[updatedPosition]));
                }
                if (e.key == "ArrowDown") {
                  e.preventDefault();
                  let updatedPosition = cycleMessagesPosition + 1;
                  if (updatedPosition >= submittedMessages.length) {
                    updatedPosition = 0;
                  }
                  setCycleMessagesPosition(updatedPosition);
                  dispatch(updateChatText(submittedMessages[updatedPosition]));
                }
              }
              if (e.key === "Enter" && e.shiftKey) {
                const prefix = e.target.value.startsWith('"') ? "" : '"';
                const suffix = e.target.value.endsWith('"') ? "" : '"';
                dispatch(updateChatText(`${prefix} e.target.value ${suffix}`));
              }
            }}
            className="chatbox"
            placeholder={
              isSaying
                ? "Enter what you wish to say."
                : "Enter what you wish to do here."
            }
          />
        </div>
        <div className="chatbox-button send" onClick={chatSubmissionHandler}>
          SEND
        </div>
      </form>
    </div>
  );
};

export default ChatInput;
