/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CUSTOM COMPONENTS */
import ReportMessageForm from "./ReportMessageForm";
/* ICONS */
import { BsFillStarFill } from "react-icons/bs";
import { BsStar } from "react-icons/bs";
import { BsReplyFill } from "react-icons/bs";
import { BsFillFlagFill } from "react-icons/bs";
import { RiReplyFill } from "react-icons/ri";
import {
  AiFillDislike,
  AiFillLike,
  AiOutlineDislike,
  AiOutlineLike,
} from "react-icons/ai";

import { ChatBubble } from "../../../../../../../components/ChatBubble/index.tsx";

const AgentMessage = ({
  text,
  actor,
  onReply,
  eventId,
  onClickFunction,
  scrollToBottom,
}) => {
  /* ------ LOCAL STATE ------ */
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
      setIsStarred(true);
    }
  };

  const reportingHandler = () => {
    setIsReporting(true);
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
    if (!showReportModal) {
      if (isReporting && reportModalSubmitted) {
        setIsReported(true);
        setIsReporting(false);
      } else {
        setIsReporting(false);
      }
    }
  }, [showReportModal]);

  return (
    <>
      <div
        className={`_agent-message_ flex flex-row justify-start items-center mb-4 mr-28
        ${inHelpMode ? "active" : ""}`}
        onClick={onClickFunction}
      >
        {isLiked ? (
          <>
            {isStarred ? (
              <BsFillStarFill className={`text-yellow-300`} />
            ) : giftXp > 0 ? (
              <Tooltip
                title="Click to ward player a Gift XP Star"
                position="top"
              >
                <BsStar className={`text-yellow-300`} onClick={starHandler} />
              </Tooltip>
            ) : null}
          </>
        ) : null}
        <div className="flex flex-col">
          <ChatBubble align="left" actor={actor.toUpperCase()} action="default">
            <div className="flex flex-col max-w-md break-words">
              <div className="mb-2">{text}</div>
              {isReported ? (
                <span className="text-error-content">
                  This Message Has been reported
                </span>
              ) : null}
              <div className="flex flex-row w-full justify-between items-center">
                <RiReplyFill
                  className="cursor-pointer hover:text-info"
                  onClick={() => onReply(actor)}
                />
                <div className="flex flex-row justify-center items-center">
                  {isDisliked ? null : (
                    <Tooltip
                      title="This message is in-character!"
                      position="bottom"
                    >
                      {isLiked ? (
                        <AiFillLike
                          className="ml-2 text-success cursor-pointer"
                          onClick={toggleLikeHandler}
                        />
                      ) : (
                        <AiOutlineLike
                          className="ml-2 text-slate-600 hover:text-success cursor-pointer"
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
                          className="ml-3 text-error cursor-pointer"
                          onClick={toggleDislikeHandler}
                        />
                      ) : (
                        <AiOutlineDislike
                          className="ml-3 text-slate-600 hover:text-error cursor-pointer"
                          onClick={toggleDislikeHandler}
                        />
                      )}
                    </Tooltip>
                  )}
                </div>
              </div>
            </div>
          </ChatBubble>
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
    </>
  );
};
export default AgentMessage;
