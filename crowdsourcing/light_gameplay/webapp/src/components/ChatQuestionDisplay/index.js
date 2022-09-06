
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import ChatMessages from "./ChatMessages";

//ChatQuestionDisplay - renders primary container for both chat and entirety of chat controls
const ChatQuestionDisplay = ({
  questionData,
  children
}) => {

  return (
    <div className="chat-wrapper">
      <div className="chat" >
        <ChatMessages
          messages={questionData}
        />
      </div>
      <div className="chat-answers">
        {children}
      </div>
    </div>
  );
};

export default ChatQuestionDisplay;
