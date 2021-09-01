import React from "react";
import "./styles.css";
//CUSTOM COMPONENTS
import Entry from "./Entry";

const ChatMessages = ({
  messages,
  agents,
  persona,
  setTextTellAgent,
  setPlayerXp,
  setPlayerGiftXp,
  playerGiftXp,
  playerXp,
  sessionGiftXpSpent,
  setSessionGiftXpSpent,
}) => {
  return (
    <div className="chatlog">
      {messages.map((msg, idx) => (
        <Entry
          key={msg.event_id}
          msg={msg}
          agents={agents}
          onReply={(agent) => {
            setTextTellAgent(agent);
          }}
          selfId={persona.id}
          setPlayerXp={setPlayerXp}
          setPlayerGiftXp={setPlayerGiftXp}
          playerGiftXp={playerGiftXp}
          playerXp={playerXp}
          sessionGiftXpSpent={sessionGiftXpSpent}
          setSessionGiftXpSpent={setSessionGiftXpSpent}
        />
      ))}
    </div>
  );
};

export default ChatMessages;
