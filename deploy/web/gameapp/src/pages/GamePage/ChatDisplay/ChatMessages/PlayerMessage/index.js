/* REACT */
import React, { useState, useEffect } from "react";
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
  console.log("CALLER:  ", caller);
  console.log("ACTOR:  ", actor);
  console.log("MESSAGE TEXT:", text);
  console.log("XP", xp);

  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----LOCAL STATE---- */
  const [formatttedMessage, setFormattedMessage] = useState("");
  const [isSay, setIsSay] = useState(false);
  const [isDo, setIsDo] = useState(false);
  const [isTell, setIsTell] = useState(false);
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    let textEndIndex = text.length - 1;
    let firstTextCharacter = text[0];
    let lastTextCharacter = text[textEndIndex];
    let firstFourTextCharacters = text.slice(0, 4);
    console.log("FIRST 4:", firstFourTextCharacters);
    if (firstTextCharacter === '"' && lastTextCharacter === '"') {
      setIsSay(true);
      setIsDo(false);
      setIsTell(false);
    } else if (firstFourTextCharacters === "tell") {
      setIsSay(false);
      setIsDo(false);
      setIsTell(true);
    } else {
      setIsSay(false);
      setIsDo(true);
      setIsTell(false);
    }
  }, [text]);

  return (
    <div
      className={` flex flex-row justify-start items-center ${
        inHelpMode ? "active" : ""
      }`}
      onClick={onClickFunction}
    >
      <span className="text-white">YOU</span>
      <div className="mx-10">
        <div
          className={`relative min-w-[120px] min-h-[90px] ${
            isSay
              ? "bg-green-700 text-white"
              : isTell
              ? "bg-red-700 text-white"
              : isDo
              ? "bg-blue-500 text-white"
              : "bg-white text-black"
          } rounded-[10px] flex justify-center items-center text-xl`}
        >
          <div className="flex flex-col max-w-md break-words">
            <p>{text}</p>
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
          <div
            className={`absolute w-0 h-0 border-t-[13px] border-t-transparent border-b-[13px] border-b-transparent border-r-[26px] ${
              isSay
                ? "border-r-green-700"
                : isTell
                ? " border-r-red-700"
                : isDo
                ? "border-r-blue-500"
                : "border-r-white"
            } right-[100%] top-[50%] translate-y-[-50%]`}
          />
        </div>
      </div>
    </div>
  );
};
export default PlayerMessage;
