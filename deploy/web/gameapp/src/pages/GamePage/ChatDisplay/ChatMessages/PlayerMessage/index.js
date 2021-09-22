/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../features/tutorials/tutorials-slice";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";
/* STYLES */
import "./styles.css";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";

//PlayerMessage - Renders message sent by player to chat with custom styling and displays any xp awarded to message
const PlayerMessage = ({ text, caller, actor, xp }) => {
  let classNames = "message type-dialogue ";
  if (["tell", "say", "whisper"].includes(caller)) {
    text = "&ldquo;" + text + "&rdquo;";
    classNames = "message type-dialogue ";
  }
  classNames += "me";

  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    dispatch(updateSelectedTip(tipNumber));
  };

  return (
    <div className={classNames}>
      <TutorialPopover
        tipNumber={0}
        open={inHelpMode && selectedTip === 0}
        position="left"
      >
        <div className="agent">
          <span id="message-nameplate">
            {actor ? actor.toUpperCase() : null}
          </span>
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
                  <span id="message-star__container">
                    <p id="message-star__number">{xp}</p>
                    <i id="message-star" className="fa fa-star" />
                  </span>
                </Tooltip>
              </>
            ) : null}
          </>
        </div>
        {text}
      </TutorialPopover>
    </div>
  );
};
export default PlayerMessage;
