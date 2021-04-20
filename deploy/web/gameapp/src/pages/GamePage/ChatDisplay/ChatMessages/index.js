import React from "react";

//CUSTOM COMPONENTS
import Entry from "./Entry";

const ChatMessages = ({ messages, agents, persona, setTextTellAgent }) => {
  return (
    <div className="chatlog">
      {messages.map((msg, idx) => (
        <Entry
          key={idx}
          msg={msg}
          agents={agents}
          onReply={(agent) => {
            setTextTellAgent(agent);
          }}
          selfId={persona.id}
        />
      ))}
    </div>
  );
};

export default ChatMessages;
