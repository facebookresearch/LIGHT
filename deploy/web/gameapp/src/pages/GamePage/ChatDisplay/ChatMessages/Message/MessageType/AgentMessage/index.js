/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* STYLES */
import "./styles.css";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import { updateSessionSpentGiftXp } from "../../../../../../../features/sessionInfo/sessionspentgiftxp-slice";
import {
  setReportModal,
  setReportModalMessageId,
  setReportModalMessage,
  setReportModalActor,
  setReportModalSubmitted,
} from "../../../../../../../features/modals/modals-slice";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CONFIG */
import CONFIG from "../../../../../../../config.js";

/* ICONS */
import { BsFillFlagFill } from "react-icons/bs";
import { RiReplyFill } from "react-icons/ri";
import { RiSingleQuotesR } from "react-icons/ri";
import {
  AiFillDislike,
  AiFillLike,
  AiOutlineDislike,
  AiOutlineLike,
} from "react-icons/ai";
/* CUSTOM COMPONENTS */
import { ChatBubble } from "../../../../../../../components/ChatBubble";
import GiftStar from "../../../../../../../components/Stars/GiftStar";


//handleReward - sends award exp to owner of message and message id to backend
function handleReward(messageId, messageOwner) {
  let base_url = window.location.protocol + "//" + CONFIG.hostname;
  if (CONFIG.port !== "80") {
    base_url += ":" + CONFIG.port;
  }

  fetch(`${base_url}/game/api/grant_reward`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "same-origin",
    body: JSON.stringify({
      target_event_id: messageId,
      target_node_id: messageOwner,
    }),
  });
}

//AgentMessage - Message component sent by another player or model.  Can be awarded xp by user if they have any gift xp.  Can open reporting modal to report message for variet of reasons.  Can be replied too by clicking the reply button.
const AgentMessage = ({
  text,
  caller,
  actor,
  onReply,
  eventId,
  actorId,
  onClickFunction,
  scrollToBottom,
}) => {
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //MODAL STATE
  const showReportModal = useAppSelector(
    (state) => state.modals.showReportModal
  );
  const reportModalMessage = useAppSelector(
    (state) => state.modals.reportModalMessage
  );
  const reportModalMessageId = useAppSelector(
    (state) => state.modals.reportModalMessageId
  );

  const reportModalSubmitted = useAppSelector(
    (state) => state.modals.reportModalSubmitted
  );
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  //GIFT XP STATE
  const giftXp = useAppSelector((state) => state.giftXp.value);

  //SESSION SPENT GIFT XP STATE
  const sessionSpentGiftXp = useAppSelector(
    (state) => state.sessionSpentGiftXp.value
  );
  /* ------ LOCAL STATE ------ */
  const [formattedText, setFormattedText] = useState("")
  const [messageAction, setMessageAction] = useState("default")
  const [isEditMode, setEditMode] = useState(false);
  const [isReporting, setIsReporting] = useState(false);
  const [isReported, setIsReported] = useState(false);
  const [isStarred, setIsStarred] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isDisliked, setIsDisliked] = useState(false);
  const [helpEventId, setHelpEventId] = useState(0);

  /* ------ HANDLERS ------ */

  const toggleLikeHandler = () => {
    let newLikeValue = !isLiked;
    setIsLiked(newLikeValue);
    scrollToBottom();
  };

  const toggleDislikeHandler = () => {
    let newDislikeValue = !isDisliked;
    setIsDisliked(newDislikeValue);
    scrollToBottom();
  };

  const starHandler = () => {
    if (giftXp >= 1) {
      let updatedSessionSpentGiftXp = sessionSpentGiftXp + 1;
      handleReward(eventId, actorId);
      setIsStarred(true);
      dispatch(updateSessionSpentGiftXp(updatedSessionSpentGiftXp));
    }
  };

  const reportingHandler = () => {
    setIsReporting(true);
    dispatch(setReportModalMessageId(eventId));
    dispatch(setReportModalMessage(text));
    dispatch(setReportModalActor(actor));
    dispatch(setReportModal(true));
    scrollToBottom();
  };

  const reportedHandler = () => {
    setIsReported(true);
    scrollToBottom(scrollToBottom);
  };

  const onAgentClick = () => {
    setHelpEventId(eventId);
    onClickFunction();
  };

  /*  LIFE CYCLE */
  useEffect(() => {
    let updatedMessage = text;
    console.log("CALLER:  ", caller)
    if(caller==="SayEvent"){
      setMessageAction("theySay")
      let saidIndex = updatedMessage.indexOf("said")
      if(saidIndex>0){
        updatedMessage = updatedMessage.slice(saidIndex+4);
      }
      updatedMessage = updatedMessage.slice(2, updatedMessage.length-1)
    }
    if(caller==="TellEvent"){
      setMessageAction("theyTell")
      let toldIndex = updatedMessage.indexOf("told you")
      updatedMessage = updatedMessage.slice(toldIndex+8, updatedMessage.length-1)
    }
    if(caller==="EmoteEvent" || caller==="ArriveEvent"){
      setMessageAction("theyDo")
    }
    setFormattedText(updatedMessage)
  }, [text]);

  useEffect(() => {
    if (!showReportModal) {
      if (isReporting && reportModalSubmitted) {
        setIsReported(true);
        setIsReporting(false);
        dispatch(setReportModalSubmitted(false));
      } else {
        setIsReporting(false);
      }
    }
  }, [showReportModal]);

  useEffect(() => {
    console.log("UPON IS REPORTING CHANGE:  ", isReporting);
  }, [isReporting]);

  return (

      <div
        className={`_agent-message-row_ flex w-full mb-4 
        ${inHelpMode ? "active" : ""}`}
        onClick={onClickFunction}
      >
        <div className="_agent-message-container_ flex flex-col max-w-[80%]">
        <div className="_chatbubble-container_ flex flex-row">
          <ChatBubble align="left" actor={actor.toUpperCase()} action={messageAction}>
            <div className="_agent-message-content_ w-full flex flex-col">
              {messageAction===theyTell?
                  <p className="text-left text-white font-bold italic opacity-50 truncate text-xs mt-1" >Told to you</p>
                  :null
              }
            <div className="_agent-message-text-container_ flex flex-row justify-between items-between">
              <p className={`_agent-message-bubble-text_ w-full  mb-2 break-words ${messageAction===theySay ? "text-black" : "text-white"}`}>{formattedText}</p>
              {isLiked ? (
            <>
              <GiftStar 
                giftXp={giftXp}
                isLiked={isLiked}
                isStarred={isStarred}
                onClick={starHandler}
              />
            </>
          ) : null}
            </div>
              {isReported ? (
                <span className="text-red-400">
                  This Message Has been reported
                </span>
              ) : null}
              <div className="_agent-message-content-footer_ flex flex-row w-full justify-between items-center">
                <RiReplyFill
                  className="_agent-message-reply-icon_ cursor-pointer hover:text-info"
                  onClick={() => onReply(actor)}
                />
                <div className="_agent-message-rating-icons_ flex flex-row justify-center items-center">
                  {isDisliked ? null : (
                    <Tooltip
                      title="This message is in-character!"
                      position="bottom"
                    >
                      {isLiked ? (
                        <AiFillLike
                          className="ml-2 text-green-400  cursor-pointer"
                          onClick={toggleLikeHandler}
                        />
                      ) : (
                        <AiOutlineLike
                          className="ml-2 text-green-400 hover:text-success cursor-pointer"
                          onClick={toggleLikeHandler}
                        />
                      )}
                    </Tooltip>
                  )}
                  {isLiked ? null : (
                    <Tooltip
                      title={
                        !isReported
                          ? "This message has issues..."
                          : "This Message has already been reported."
                      }
                      position="bottom"
                    >
                      {isDisliked ? (
                        <AiFillDislike
                          className="ml-3 text-red-400 cursor-pointer"
                          onClick={toggleDislikeHandler}
                        />
                      ) : (
                        <AiOutlineDislike
                          className="ml-3 text-red-400 hover:text-error cursor-pointer"
                          onClick={toggleDislikeHandler}
                        />
                      )}
                    </Tooltip>
                  )}
                </div>
              </div>
            </div>
          </ChatBubble>
          {
            (messageAction === "theySay" ||  messageAction === "theyTell")?
          <div className="_quote-container_ relative  w-[1px] h-full">
            <RiSingleQuotesR size={38} className={`_quote-icon-stroke_ absolute ${messageAction === "theyTell" ? "text-info": messageAction === "theyDo" ? "text-red-100" : "text-white"} -left-[30px] -top-[16px] z-38`} />
            <RiSingleQuotesR size={34} className="_quote-icon_ absolute text-black -left-[28px] -top-[14px] z-40" />
            <RiSingleQuotesR size={38} className={`_quote-icon-stroke_ absolute ${messageAction === "theyTell" ? "text-info": messageAction === "theyDo" ? "text-red-100" : "text-white"} -left-[20px] -top-[16px] z-38`} />
            <RiSingleQuotesR size={34} className="_quote-icon_ absolute text-black -left-[18px] -top-[14px] z-40" />
          </div> :
            null
          }
          </div>
          <div className="w-full flex justify-start items-start">
            {isLiked && !isStarred ? (
              giftXp > 0 ? (
                <div
                  className="text-right text-yellow-500 break-words text-sm mt-1 cursor-pointer"
                  onClick={starHandler}
                >
                  Would you like to award this message a star?
                </div>
              ) : (
                <div className="text-right text-base-200 opacity-50 break-words text-sm mt-1">
                  Earn gift experience by roleplaying to be able to award stars
                </div>
              )
            ) : null}
            {isDisliked && !isReported ? (
              <div
                className="text-right text-red-500 break-words text-sm mt-1 cursor-pointer"
                onClick={reportingHandler}
              >
                <BsFillFlagFill className="inline-block mr-2" />
                <span className="inline-block">Report this message</span>
              </div>
            ) : null}
          </div>
        </div>
      </div>
  );
};
export default AgentMessage;
