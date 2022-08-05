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
  // let classNames = "message type-dialogue ";
  // if (["tell", "say", "whisper"].includes(caller)) {
  //   text = "&ldquo;" + text + "&rdquo;";
  //   classNames = "message type-dialogue ";
  // }
  // classNames += "me";

  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  return (
    <div
      className={` flex flex-row justify-start items-center  ${
        inHelpMode ? "active" : ""
      }`}
      onClick={onClickFunction}
    >
      <span className="text-white">YOU</span>
      <div className="mx-10">
        <div className="relative min-w-[120px] min-h-[90px] bg-white rounded-[10px] flex justify-center items-center text-black text-xl">
          <div className="flex flex-col">
            {text}
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
          <div className="relative">
            <div className="absolute bg-emerald-500">
              <TutorialPopover
                tipNumber={17}
                open={inHelpMode && selectedTip === 17}
                position="top"
              ></TutorialPopover>
            </div>
          </div>
          <div className="absolute w-0 h-0 border-t-[13px] border-t-transparent border-b-[13px] border-b-transparent border-r-[26px] border-r-white right-[100%] top-[50%] translate-y-[-50%]" />
        </div>
      </div>
    </div>
  );
};
export default PlayerMessage;
