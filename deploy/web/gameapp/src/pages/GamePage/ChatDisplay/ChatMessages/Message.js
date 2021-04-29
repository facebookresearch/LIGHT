import React, { useState } from "react";

import "../../styles.css";
import { Tooltip } from "react-tippy";
import CONFIG from "../../../../config.js";

function handleReport(reportedMessage, reportReason) {
  let base_url = window.location.protocol + "//" + CONFIG.hostname;
  if (CONFIG.port != "80") {
    base_url += ":" + CONFIG.port;
  }

  fetch(`${base_url}/report`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "same-origin",
    body: JSON.stringify({
      message: reportedMessage,
      reason: reportReason,
    }),
  });
}

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

const Message = ({
  text,
  caller,
  actor,
  isSelf,
  onReply,
  setPlayerXp,
  setPlayerGiftXp,
  playerGiftXp,
  playerXp,
  xp,
  eventId,
  actorId,
  sessionGiftXpSpent,
  setSessionGiftXpSpent,
}) => {
  const [isEditMode, setEditMode] = React.useState(false);
  const [isReportMode, setReportMode] = React.useState(false);
  const [reportReason, setReportReason] = React.useState("");
  const [isReported, setReported] = React.useState(false);
  const [isLiked, setIsLiked] = React.useState(false);

  const likeHandler = () => {
    if (playerGiftXp >= 1) {
      handleReward(eventId, actorId);
      setIsLiked(true);
      setSessionGiftXpSpent(sessionGiftXpSpent + 1);
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
            <React.Fragment>
              <i className="fa fa-reply" onClick={() => onReply(actor)} />{" "}
              <i
                className="fa fa-commenting-o "
                onClick={() => setEditMode(false)}
              />
            </React.Fragment>
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

  if (isReportMode) {
    return (
      <div className={classNames}>
        <div className="agent">
          <span>{actor}</span>
        </div>
        {text}
        <div>
          <b>Why are you reporting this message?</b>
        </div>
        <input
          className="edit-message"
          defaultValue={"Enter reason here"}
          value={reportReason}
          onChange={(evt) => setReportReason(evt.target.value)}
        />
        <button
          type="submit"
          disabled={reportReason.length == 0}
          onClick={() => {
            handleReport(text, reportReason);
            setReportReason("");
            setReported(true);
            setReportMode(false);
          }}
        >
          Report
        </button>
        <button
          type="submit"
          onClick={() => {
            setReportMode(false);
          }}
        >
          Cancel
        </button>
      </div>
    );
  }

  if (isReported) {
    return (
      <div className={classNames}>
        <div className="agent">
          <span>{actor}</span>
        </div>
        <i>We have logged your report of this message</i>
      </div>
    );
  }

  return (
    <div className={classNames}>
      {actor ? (
        <div className="agent">
          <span style={{ fontFamily: "fantasy" }}>
            {actor ? actor.toUpperCase() : null}
          </span>
          {isSelf ? (
            <React.Fragment>
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
                      }}
                    >
                      {xp}
                      <i className="fa fa-star message-star" />
                    </span>
                  </Tooltip>
                </>
              ) : null}
            </React.Fragment>
          ) : (
            <React.Fragment>
              <span style={{ backgroundColor: "white" }}>
                <Tooltip
                  title={
                    playerGiftXp > 0
                      ? `Award ${actor} Experience`
                      : "Not enough Gift Experience"
                  }
                  position="top"
                >
                  {isLiked ? (
                    <i className="fa fa-star message-star" />
                  ) : (
                    <i className="fa fa-star-o" onClick={likeHandler} />
                  )}
                </Tooltip>{" "}
                <Tooltip title={`tell ${actor}...`} position="top">
                  <i className="fa fa-reply" onClick={() => onReply(actor)} />
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
                    className="fa fa-flag "
                    onClick={() => setReportMode(true)}
                  />
                </Tooltip>
              </span>
            </React.Fragment>
          )}
        </div>
      ) : null}
      {text}
    </div>
  );
};
export default Message;
