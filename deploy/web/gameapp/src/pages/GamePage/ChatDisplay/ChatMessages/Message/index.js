/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, {useState, useEffect} from "react";
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../features/tutorials/tutorials-slice";
/* MESSAGE COMPONENTS */
import PlayerMessage from "./MessageType/PlayerMessage";
import AgentMessage from "./MessageType/AgentMessage";
import InventoryMessage from "./MessageType/InventoryMessage";
import MissionCompleteMessage from "./MessageType/MissionCompleteMessage";
import HelpMessage from "./MessageType/HelpMessage";
import SettingMessage from "./MessageType/SettingMessage";
import SoulSpawnEventMessage from "./MessageType/SoulSpawnEventMessage";
import StatusMessage from "./MessageType/StatusMessage";
import QuestMessage from "./MessageType/QuestMessage";

/* UTIL */
//get_msg_actor - helper function that retrieves actor sending message.
function get_msg_actor(msg) {
  if (msg.actors === undefined) {
    return msg.actor.node_id;
  } else {
    return msg.actors[0];
  }
}

//Message - Renders specific type of message component based on individual message object's attributes
const Message = ({messageId, selectedMessage,  msg, onReply, agents, selfId, scrollToBottom, selectMessage }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
      dispatch(updateSelectedTip(tipNumber));
  }
  /* ----LOCAL STATE---- */
  const [isSelected, setIsSelected] = useState(false);
  /* ---- LIFECYCLE---- */
  useEffect(()=>{
    if(messageId === selectedMessage){
      setIsSelected(true);
    }else {
      setIsSelected(false);
    }
  },[selectedMessage])
  /* ----HANDLERS---- */
  const messageClickHandler = ( tipNumber)=>{
    if (inHelpMode) {
      setSelectedTip(tipNumber);
      selectMessage(messageId);
    };
  };
  if (
    [
      "LookEvent",
      "GoEvent",
      "ExamineEvent",
      "ErrorEvent",
      "HelpEvent",
      "text",
      "InventoryEvent",
      "HealthEvent",
      "QuestEvent",
    ].includes(msg.caller) ||
    msg.caller === null
  ) {
    if (msg.caller === "HelpEvent") {
      return (
        <HelpMessage
          isSelected={isSelected}
          text={msg.text}
          onClickFunction={() => messageClickHandler(10)}
        />
      );
    } else if (msg.caller === "InventoryEvent") {
      return (
        <InventoryMessage
          isSelected={isSelected}
          text={msg.text}
          onClickFunction={() => messageClickHandler(11)}
        />
      );
    } else if (msg.caller === "HealthEvent") {
      return (
        <StatusMessage
          isSelected={isSelected}
          text={msg.text}
          onClickFunction={() => messageClickHandler(12)}
        />
      );
    } else if (msg.caller === "QuestEvent") {
      return (
        <QuestMessage
          isSelected={isSelected}
          text={msg.text}
          onClickFunction={() => messageClickHandler(13)}
        />
      );
    } else {
      return (
        <SettingMessage
          isSelected={isSelected}
          text={msg.text}
          onClickFunction={() => messageClickHandler(15)}
        />
      );
    }
  } else {
    var actor = get_msg_actor(msg);
    return (
      <>
        {msg.caller === "SoulSpawnEvent" ? (
          <SoulSpawnEventMessage
            isSelected={isSelected}
            text={msg.text}
            onClickFunction={() => messageClickHandler(9)}
          />
        ) : msg.questComplete ? (
          <MissionCompleteMessage
            isSelected={isSelected}
            xp={msg.xp}
            name={msg.text}
            onClickFunction={() => messageClickHandler(14)}
          />
        ) : msg.is_self || actor === selfId ? (
          <PlayerMessage
            isSelected={isSelected}
            text={msg.text}
            isSelf={msg.is_self || actor === selfId}
            caller={msg.caller}
            actor={agents[actor]}
            onReply={onReply}
            xp={msg.xp}
            onClickFunction={() => messageClickHandler(17)}
          />
        ) : (
          <AgentMessage
            isSelected={isSelected}
            text={msg.text}
            caller={msg.caller}
            actor={agents[actor]}
            onReply={onReply}
            xp={msg.xp}
            actorId={actor}
            eventId={msg.event_id}
            onClickFunction={() => messageClickHandler(16)}
            scrollToBottom={scrollToBottom}
          />
        )}
      </>
    );
  }
};

export default Message;
