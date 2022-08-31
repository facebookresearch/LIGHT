/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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

const HelpMessage = ({ text, onClickFunction }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
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
      <div
        className={`help-content ${inHelpMode ? "active" : ""}`}
        onClick={onClickFunction}
      >
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
          <TutorialPopover
            tipNumber={10}
            open={inHelpMode && selectedTip === 10}
            position="bottom"
          />
        </div>
      </div>
    </div>
  );
};
export default HelpMessage;
