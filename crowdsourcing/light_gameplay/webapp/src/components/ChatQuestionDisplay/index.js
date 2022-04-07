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
