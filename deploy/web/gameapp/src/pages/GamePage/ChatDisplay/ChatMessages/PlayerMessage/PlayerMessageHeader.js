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
const PlayerMessageHeader = ({}) => {
  return (
    <div>
      <div className="agent">
        <span id="message-nameplate">{actor ? actor.toUpperCase() : null}</span>
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
      </div>
    </div>
  );
};
export default PlayerMessage;
