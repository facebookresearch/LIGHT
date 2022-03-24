/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

// ChatInputOption - Component that renders chat bar along with Say/Do buttons and send button
const ChatInputOption = ({
  answer
}) => {
  const {isSaying, text, isCorrect} = answer;
  return (
    <div className="chatbar-container">
        <div className="chatbar">
          <div
            className={`chatbox-button ${
              isSaying ? "say" : "do"
            } `}
          >
          </div>
            <input
              className={`chatbox-input`}
              value={text}
            />
        </div>
        <div
          className="chatbox-button send"
        >
          SEND
        </div>
    </div>
  );
};

export default ChatInputOption;
