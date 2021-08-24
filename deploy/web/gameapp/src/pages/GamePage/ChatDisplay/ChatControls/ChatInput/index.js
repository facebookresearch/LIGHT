//REACT
import React, { useState } from "react";
//STYLES
import "./styles.css";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatInput = ({
  onSubmit,
  enteredText,
  setEnteredText,
  chatInputRef,
  scrollToBottom,
  resetIdleTimer,
  isSaying,
  toggleIsSaying,
  tellTarget,
}) => {
  /*---------------HANDLERS----------------*/
  const chatSubmissionHandler = (e) => {
    e.preventDefault();
    let textSubmission;
    if (!!enteredText) {
      if (tellTarget !== null) {
        textSubmission = `"tell ${tellTarget} ${enteredText}"`;
      } else if (isSaying) {
        textSubmission = `"${enteredText}"`;
      } else {
        textSubmission = enteredText;
      }
      console.log("TEXT SUBMISSION:  ", textSubmission);
      onSubmit(textSubmission);
      setEnteredText("");
      scrollToBottom();
    }
  };

  /*---------------HELPERS----------------*/
  const formatTellTargetForButton = (str) => {
    let formattedTellTargetName = str.toUpperCase();
    if (str.length > 10) {
      formattedTellTargetName = ` ${formattedTellTargetName.slice(0, 10)}...`;
    }
    return formattedTellTargetName;
  };

  return (
    <form style={{ display: "flex" }} onSubmit={chatSubmissionHandler}>
      <div
        className={`chatbox-button ${isSaying ? "say" : "do"}`}
        onClick={(e) => {
          e.preventDefault();
          toggleIsSaying();
        }}
      >
        {tellTarget !== null
          ? `TELL ${formatTellTargetForButton(tellTarget)}`
          : isSaying
          ? "SAY"
          : "DO"}
      </div>
      <input
        className="chatbox-input"
        ref={chatInputRef}
        value={enteredText}
        onChange={(e) => {
          resetIdleTimer();
          setEnteredText(e.target.value);
        }}
        onKeyDown={(e) => {
          if (e.key == "`") {
            e.preventDefault();
            toggleIsSaying();
          }
        }}
        onKeyPress={(e) => {
          if (e.key === "Enter" && e.shiftKey) {
            const prefix = e.target.value.startsWith('"') ? "" : '"';
            const suffix = e.target.value.endsWith('"') ? "" : '"';
            setEnteredText(prefix + e.target.value + suffix);
          }
        }}
        className="chatbox"
        placeholder={
          isSaying
            ? "Enter what you wish to say."
            : "Enter what you wish to do here."
        }
      />
      <div className="chatbox-button send" onClick={chatSubmissionHandler}>
        SEND
      </div>
    </form>
  );
};

export default ChatInput;
