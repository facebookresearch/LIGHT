/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
            {
              isSaying ? "SAY" : "DO"
            }
          </div>
            <input
              className={`chatbox-input`}
              value={text}
            />
        <div
          className="chatbox-button send"
        >
          SEND
        </div>
      </div>

    </div>
  );
};

export default ChatInputOption;
