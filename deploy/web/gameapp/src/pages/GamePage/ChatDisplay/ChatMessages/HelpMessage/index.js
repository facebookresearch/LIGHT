/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* ICONS */
import { FaQuestion } from "react-icons/fa";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

const HelpMessage = ({ text }) => {
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
  /* ---- LOCAL STATE ---- */
  const [commandList, setCommandList] = useState([]);
  /* ---- LIFECYCLE ---- */
  useEffect(() => {
    let commandArr = text.split("\n");
    commandArr = commandArr.slice(5, commandArr.length - 2);
    setCommandList(commandArr);
  }, [text]);

  return (
    <div className=" help-container">
      <div className="help-question__container">
        <FaQuestion className="help-question" color="#0072ff" />
      </div>
      <div className="help-content">
        <p className="help-content__header">COMMANDS</p>
        <div className="help-content__entries">
          {commandList.map((command, index) => {
            return (
              <p
                key={index}
                className="help-content__entry"
                style={{ margin: "10px 0 0 0" }}
              >
                {command}
              </p>
            );
          })}
        </div>
      </div>
    </div>
  );
};
export default HelpMessage;
