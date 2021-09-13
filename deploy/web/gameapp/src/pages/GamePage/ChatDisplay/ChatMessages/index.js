/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import { updateTellTarget } from "../../../../features/chatInput/chatinput-slice";
/* STYLES */
import "./styles.css";
//CUSTOM COMPONENTS
import Entry from "./Entry";

const ChatMessages = ({
  messages,
  setPlayerXp,
  setPlayerGiftXp,
  playerGiftXp,
  playerXp,
  sessionGiftXpSpent,
  setSessionGiftXpSpent,
}) => {
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //AGENTS STATE
  const agents = useAppSelector((state) => state.agents);
  //PERSONA STATE
  const persona = useAppSelector((state) => state.persona);

  return (
    <>
      {messages.map((msg, idx) => (
        <div className="message-row">
          <Entry
            key={msg.event_id}
            msg={msg}
            agents={agents}
            onReply={(agent) => {
              dispatch(updateTellTarget(agent));
            }}
            selfId={persona.id}
            setPlayerXp={setPlayerXp}
            setPlayerGiftXp={setPlayerGiftXp}
            playerGiftXp={playerGiftXp}
            playerXp={playerXp}
            sessionGiftXpSpent={sessionGiftXpSpent}
            setSessionGiftXpSpent={setSessionGiftXpSpent}
          />
        </div>
      ))}
    </>
  );
};

export default ChatMessages;
