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
  

  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);

  return (
    <div
      className={`flex flex-row items-center ${inHelpMode ? "active" : ""}`}
      onClick={onClickFunction}
    >
      <div className="agent text-white mr-4">
          <span id="_message-nameplate">
            {/* {actor ? actor.toUpperCase() : null} */}
            You
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
      <TutorialPopover
        tipNumber={17}
        open={inHelpMode && selectedTip === 17}
        position="top"
      >
        <div className="btn bg-white border-0 border-l-4 border-purple-600 text-black">{text}</div>
      </TutorialPopover>
    </div>
  );
};
export default PlayerMessage;
