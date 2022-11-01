/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState } from "react";
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
  actor,
  scrollToBottom,
  ratingStepHandler,
}) => {
  /* ------ LOCAL STATE ------ */
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

  return (
    <>
      <div
        className={`_agent-message_ flex flex-row justify-start items-center mb-4 mr-28`}
      >
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
                {introStep >= 3 ? (
                  <div className="flex flex-row justify-center items-center">
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
    </>
  );
};
export default AgentMessage;
