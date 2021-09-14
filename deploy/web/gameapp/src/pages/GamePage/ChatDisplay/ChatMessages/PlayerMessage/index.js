/* REACT */
import React, { useState } from "react";
/* STYLES */
import "./styles.css";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import { updateSessionSpentGiftXp } from "../../../../../features/sessionInfo/sessionspentgiftxp-slice";
//TOOLTIP
import { Tooltip } from "react-tippy";
//CONFIG
import CONFIG from "../../../../../config.js";

function handleReward(messageId, messageOwner) {
  let base_url = window.location.protocol + "//" + CONFIG.hostname;
  if (CONFIG.port != "80") {
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

const PlayerMessage = ({
  text,
  caller,
  actor,
  isSelf,
  onReply,
  playerGiftXp,
  xp,
  eventId,
  actorId,
}) => {
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //SESSION XP STATE

  //SESSION SPENT GIFT XP STATE
  const sessionSpentGiftXp = useAppSelector(
    (state) => state.sessionSpentGiftXp.value
  );
  /* REDUX ACTIONS */
  /* ------ LOCAL STATE ------ */
  const [isEditMode, setEditMode] = React.useState(false);
  const [isReportMode, setReportMode] = React.useState(false);
  const [reportReason, setReportReason] = React.useState("");
  const [isReported, setReported] = React.useState(false);
  const [isLiked, setIsLiked] = React.useState(false);

  const likeHandler = () => {
    if (playerGiftXp >= 1) {
      handleReward(eventId, actorId);
      setIsLiked(true);
      dispatch(updateSessionSpentGiftXp(sessionSpentGiftXp + 1));
    }
  };

  let classNames = "message type-dialogue ";
  if (["tell", "say", "whisper"].includes(caller)) {
    text = "&ldquo;" + text + "&rdquo;";
    classNames = "message type-dialogue ";
  }
  classNames += isSelf ? "me" : "other";

  if (isEditMode) {
    return (
      <div className={classNames}>
        <div className="agent">
          <span>{actor}</span>
          {isSelf ? null : (
            <>
              <i className="fa fa-reply" onClick={() => onReply(actor)} />{" "}
              <i
                className="fa fa-commenting-o "
                onClick={() => setEditMode(false)}
              />
            </>
          )}
        </div>
        <div style={{ opacity: 0, height: 1, pointerEvents: "none" }}>
          {text}
        </div>
        <input className="edit-message" defaultValue={text} />
        <button type="submit" onClick={() => setEditMode(false)}>
          Suggest edit
        </button>
        <button type="submit" onClick={() => setEditMode(false)}>
          Suggest edit
        </button>
      </div>
    );
  }

  return (
    <div className={classNames}>
      {actor ? (
        <div className="agent">
          <span id="message-nameplate">
            {actor ? actor.toUpperCase() : null}
          </span>
          {isSelf ? (
            <>
              {xp ? (
                <>
                  <Tooltip
                    title={
                      xp > 0
                        ? `${xp} Experience Points Earned For Roleplaying`
                        : null
                    }
                  >
                    <span
                      style={{
                        fontFamily: "fantasy",
                        backgroundColor: "white",
                        color: "gold",
                        position: "relative",
                        paddingLeft: "40px",
                      }}
                    >
                      <p id="message-star__number">{xp}</p>
                      <i className="fa fa-star message-star" />
                    </span>
                  </Tooltip>
                </>
              ) : null}
            </>
          ) : (
            <div className="message-icon__container">
              <Tooltip
                title={
                  playerGiftXp > 0
                    ? `Award ${actor} Experience`
                    : "Not enough Gift Experience"
                }
                position="top"
              >
                <div style={{ position: "relative", marginRight: "150%" }}>
                  {isLiked ? (
                    <i id="message-star" className="fa fa-star message-star" />
                  ) : (
                    <i
                      id="message-star-O"
                      className="fa fa-star-o "
                      onClick={likeHandler}
                    />
                  )}
                </div>
              </Tooltip>{" "}
              <Tooltip title={`tell ${actor}...`} position="top">
                <i
                  className="fa fa-reply message-icon"
                  onClick={() => onReply(actor)}
                />
              </Tooltip>{" "}
              {/* <Tooltip
                  title={`Do you think something else should have been said instead? Provide feedback via an edit...`}
                  position="top"
                >
                  <i
                    className="fa fa-commenting-o "
                    onClick={() => setEditMode(true)}
                  />
                </Tooltip> */}
              <Tooltip
                title={`Was this offensive or inappropriate? Click to report.`}
                position="top"
              >
                <i
                  className="fa fa-flag message-icon"
                  onClick={() => setReportMode(true)}
                />
              </Tooltip>
            </div>
          )}
        </div>
      ) : null}
      {text}
    </div>
  );
};
export default PlayerMessage;
