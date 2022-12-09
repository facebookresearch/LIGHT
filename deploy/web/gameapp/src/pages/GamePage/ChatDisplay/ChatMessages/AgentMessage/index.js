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
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import { updateSessionSpentGiftXp } from "../../../../../features/sessionInfo/sessionspentgiftxp-slice";
import {
  setReportModal,
  setReportModalMessageId,
  setReportModalMessage,
  setReportModalActor,
  setReportModalSubmitted,
} from "../../../../../features/modals/modals-slice";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CUSTOM COMPONENTS */
import ReportMessageForm from "./ReportMessageForm";
import TutorialPopover from "../../../../../components/TutorialPopover";
/* CONFIG */
import CONFIG from "../../../../../config.js";

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

import { ChatBubble } from "../../../../../components/ChatBubble";

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
    console.log("UPON SHOWREPORT MODAL CHANGE");
    console.log("reportModalSubmitted:  ", reportModalSubmitted);
    console.log("isReporting:  ", isReporting);
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

  // if (isEditMode) {
  //   return (
  //     <div className="">
  //       <div className="agent">
  //         <span>{actor}</span>
  //         <>
  //           <i className="fa fa-reply" onClick={() => onReply(actor)} />{" "}
  //           <i
  //             className="fa fa-commenting-o "
  //             onClick={() => setEditMode(false)}
  //           />
  //         </>
  //       </div>
  //       <div style={{ opacity: 0, height: 1, pointerEvents: "none" }}>
  //         {text}
  //       </div>
  //       <input className="edit-message" defaultValue={text} />
  //       <button type="submit" onClick={() => setEditMode(false)}>
  //         Suggest edit
  //       </button>
  //       <button type="submit" onClick={() => setEditMode(false)}>
  //         Suggest edit
  //       </button>
  //     </div>
  //   );
  // }

  // if (isReportMode) {
  //   return (
  //     <ReportMessageForm
  //       eventId={eventId}
  //       reportedMessage={text}
  //       caller={caller}
  //       actor={actor}
  //       exitReportMode={exitReportMode}
  //       reportedHandler={reportedHandler}
  //     />
  //   );
  // }

  // if (isReported) {
  //   return (
  //     <div className={classNames}>
  //       <div className="agent">
  //         <span>{actor}</span>
  //       </div>
  //       <i>We have logged your report of this message</i>
  //     </div>
  //   );
  // }

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

//     //   className={`${classNames} ${inHelpMode ? "active" : ""}`}
//     //   onClick={onAgentClick}
//     // >
//     //   {actor ? (
//     //     <div className="agent">
//     //       <span id="message-nameplate">
//     //         {actor ? actor.toUpperCase() : null}
//     //       </span>
//     //       {
//     //         <div className="message-icon__container">
//     //           <Tooltip
//     //             title={
//     //               giftXp > 0
//     //                 ? `Award ${actor} Experience`
//     //                 : "Not enough Gift Experience"
//     //             }
//     //             position="top"
//     //           >
//     //             <div style={{ position: "relative", marginRight: "150%" }}>
//     //               {isLiked ? (
//     //                 <i id="message-star" className="fa fa-star message-star" />
//     //               ) : (
//     //                 <i
//     //                   id="message-star-O"
//     //                   className="fa fa-star-o "
//     //                   onClick={likeHandler}
//     //                 />
//     //               )}
//     //             </div>
//     //           </Tooltip>{" "}
//     //           <Tooltip title={`tell ${actor}...`} position="top">
//     //             <i
//     //               className="fa fa-reply message-icon"
//     //               onClick={() => onReply(actor)}
//     //             />
//     //           </Tooltip>{" "}
//     //           {/* <Tooltip
//     //               title={`Do you think something else should have been said instead? Provide feedback via an edit...`}
//     //               position="top"
//     //             >
//     //               <i
//     //                 className="fa fa-commenting-o "
//     //                 onClick={() => setEditMode(true)}
//     //               />
//     //             </Tooltip> */}
//     //           <Tooltip
//     //             title={`Was this offensive or inappropriate? Click to report.`}
//     //             position="top"
//     //           >
//     //             <i
//     //               className="fa fa-flag message-icon"
//     //               onClick={() => setReportMode(true)}
//     //             />
//     //           </Tooltip>
//     //         </div>
//   // }
//       // ) : null}
//       // <TutorialPopover
//       //   tipNumber={16}
//       //   open={helpEventId === eventId && inHelpMode && selectedTip === 16}
//       //   position="bottom"
//       // >
//       //   {text}
//       // </TutorialPopover>
//     // </div>
//   );
// };

// function handleReport(reportedMessage, reportReason, reportCategory) {
//   let base_url = window.location.protocol + "//" + CONFIG.hostname;
//   if (CONFIG.port !== "80") {
//     base_url += ":" + CONFIG.port;
//   }

//   fetch(`${base_url}/report`, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     credentials: "same-origin",
//     body: JSON.stringify({
//       category: reportCategory,
//       message: reportedMessage,
//       reason: reportReason,
//     }),
//   });
// }
