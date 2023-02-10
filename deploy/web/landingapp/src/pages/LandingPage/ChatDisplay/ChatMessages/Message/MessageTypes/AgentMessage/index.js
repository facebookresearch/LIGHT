/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* CUSTOM COMPONENTS */
import { ChatBubble } from "../../../../../../../components/ChatBubble/index.tsx";
/* ICONS */
import {
  AiFillDislike,
  AiFillLike,
  AiOutlineDislike,
  AiOutlineLike,
} from "react-icons/ai";

//AgentMessage - Renders message from other players/models.  Contains buttons that allow for user feedback to the content of the message.
const AgentMessage = ({
  introStep,
  text,
  action,
  actor,
  scrollToBottom,
  ratingStepHandler,
}) => {
  /* ------ LOCAL STATE ------ */
  const [messageAction, setMessageAction] = useState("default")
  const [isReported, setIsReported] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isDisliked, setIsDisliked] = useState(false);

  /* ------ HANDLERS ------ */
  //Handles clicking on like button
  const toggleLikeHandler = () => {
    let newLikeValue = !isLiked;
    setIsLiked(newLikeValue);
    ratingStepHandler();
    scrollToBottom();
  };
  //Handles clicking on dislike button
  const toggleDislikeHandler = () => {
    let newDislikeValue = !isDisliked;
    setIsDisliked(newDislikeValue);
    ratingStepHandler();
    scrollToBottom();
  };

    /*  LIFE CYCLE */
    useEffect(() => {
      console.log("action:  ", action)
      console.log("actor:  ", actor)
      if(action==="say"){
        setMessageAction("theySay")
      }
      if(action==="do"){
        setMessageAction("theyDo")
      }
    }, [text]);
  

  //Mysterious Figure
  return (
    <>
      <div className={`_agent-message-row_ flex w-full mb-4 `}>
        <div className="_agent-message-container_ flex flex-col max-w-[80%]">
          <div className="_chatbubble-container_">
          <ChatBubble align="left" actor={actor.toUpperCase()} action={messageAction}>
            <div className="flex flex-col break-words">
              <div className="mb-2 break-words">{text}</div>
              {isReported ? (
                <span className="text-error-content">
                  This Message Has been reported
                </span>
              ) : null}
              <div className="_agent-message-content-footer_ flex flex-row w-full justify-between items-center">
                {introStep >= 3 ? (
                  <div className="_agent-message-rating-icons_ flex flex-row justify-center items-center">
                    {isDisliked ? null : isLiked ? (
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
                    {isLiked ? null : isDisliked ? (
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
                  </div>
                ) : null}
              </div>
            </div>
          </ChatBubble>
        </div>
        </div>
      </div>
    </>
  );
};
export default AgentMessage;
