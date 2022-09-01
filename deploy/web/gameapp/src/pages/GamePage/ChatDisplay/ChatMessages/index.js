/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
const ChatMessages = ({ messages, scrollToBottom }) => {
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
        <div className="_chat-message_" key={msg.event_id}>
          <Entry
            msg={msg}
            agents={agents}
            onReply={(agent) => {
              dispatch(updateTellTarget(agent));
            }}
            selfId={persona.id}
            scrollToBottom={scrollToBottom}
          />
        </div>
      ))}
    </>
  );
};

export default ChatMessages;
