//REACT
import React, { useState } from "react";
//STYLES
import "./styles.css";

// ChatInput -
const ChatInput = ({
  onSubmit,
  enteredText,
  setEnteredText,
  chatInputRef,
  scrollToBottom,
  resetIdleTimer,
}) => {
  const [isSaying, setIsSaying] = useState(true);

  const handleIsSayingToggle = (e) => {
    setIsSaying(!isSaying);
  };

  return (
    <form
      style={{ display: "flex" }}
      onSubmit={(e) => {
        e.preventDefault();

        if (!!enteredText) {
          onSubmit(enteredText);
          setEnteredText("");
          scrollToBottom();
        }
      }}
    >
      <div
        className={`chatbox-button ${isSaying ? "say" : "do"}`}
        onClick={(e) => {
          e.preventDefault();
          handleIsSayingToggle();
        }}
      >
        {isSaying ? "SAY" : "DO"}
      </div>
      <input
        className="chatbox-input"
        ref={chatInputRef}
        value={enteredText}
        onChange={(e) => {
          resetIdleTimer();
          setEnteredText(e.target.value);
        }}
        onKeyPress={(e) => {
          if (e.key == "Tab" && e.shiftKey) {
            e.preventDefault();
            handleIsSayingToggle();
          }
          if (e.key === "Enter" && e.shiftKey) {
            const prefix = e.target.value.startsWith('"') ? "" : '"';
            const suffix = e.target.value.endsWith('"') ? "" : '"';
            setEnteredText(prefix + e.target.value + suffix);
          }
        }}
        className="chatbox"
        placeholder="Enter text to interact with the world here..."
      />
      <div
        className="chatbox-button send"
        onClick={(e) => {
          e.preventDefault();

          if (!!enteredText) {
            onSubmit(enteredText);
            setEnteredText("");
            scrollToBottom();
          }
        }}
      >
        SEND
      </div>
    </form>
  );
};

export default ChatInput;
