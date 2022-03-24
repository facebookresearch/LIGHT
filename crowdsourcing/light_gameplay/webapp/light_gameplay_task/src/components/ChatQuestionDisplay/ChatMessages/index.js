/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import Entry from "./Entry";

//ChatMessages - Renders messages in chat display by iterating through message reducer returning Entry components
const ChatMessages = ({
  messages
 }) => {
  return (
    <>
      {messages.map((msg, idx) => (
        <div className="message-row" key={idx}>
          <Entry
            msg={msg.text}
            speaker={msg.speaker}
            isPlayer={msg.player}
          />
        </div>
      ))}
    </>
  );
};

export default ChatMessages;
