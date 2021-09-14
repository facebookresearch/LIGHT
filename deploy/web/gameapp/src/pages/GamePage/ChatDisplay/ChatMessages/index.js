/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import { updateTellTarget } from "../../../../features/chatInput/chatinput-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import Entry from "./Entry";

//ChatMessages - Renders messages in chat display by iterating through message reducer returning Entry components
const ChatMessages = ({ messages }) => {
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
        <div className="message-row" key={msg.event_id}>
          <Entry
            msg={msg}
            agents={agents}
            onReply={(agent) => {
              dispatch(updateTellTarget(agent));
            }}
            selfId={persona.id}
          />
        </div>
      ))}
    </>
  );
};

export default ChatMessages;
