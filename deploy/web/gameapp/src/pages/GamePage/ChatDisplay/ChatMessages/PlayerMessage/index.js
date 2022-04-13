/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

//PlayerMessage - Renders message sent by player to chat with custom styling and displays any xp awarded to message
const PlayerMessage = ({ text, caller, actor, xp, onClickFunction }) => {

  /*
  let classNames = "message type-dialogue ";
  if (["tell", "say", "whisper"].includes(caller)) {
    text = "&ldquo;" + text + "&rdquo;";
    classNames = "message type-dialogue ";
  }
  classNames += "me";
  */

  // Let's test tailwind.css here!
  const classNames = "inline-flex items-center px-2.5 py-0.5 rounded-l text-sm font-medium bg-indigo-400 text-yellow-200";

  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);

  return (
    <div
      className={`${classNames} ${inHelpMode ? "active" : ""}`}
      onClick={onClickFunction}
    >
      <TutorialPopover
        tipNumber={17}
        open={inHelpMode && selectedTip === 17}
        position="top"
      >
        <div className="agent">
          <span id="message-nameplate text-white">
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
