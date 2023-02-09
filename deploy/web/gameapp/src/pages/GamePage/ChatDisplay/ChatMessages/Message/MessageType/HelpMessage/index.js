/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppSelector } from "../../../../../../../app/hooks";
/* STYLES */
import "./styles.css";
/* ICONS */

/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../../components/TutorialPopover";

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
    <div className="_message-row_ w-full flex justify-center items-center mb-4">
      <TutorialPopover
        tipNumber={10}
        open={inHelpMode && selectedTip === 10}
        position="bottom"
      >
        <div
          className={`_help-container_ ${
            inHelpMode ? "active" : ""
          } flex border-solid border-4 rounded border-white justify-center items-center p-4 `}
          onClick={onClickFunction}
        >
          <div className="_help-content_ prose text-white text-center text-md">
            <p className="_help-content-header_ font-bold">COMMANDS</p>
            {commandList.map((command, index) => {
              let formattedCommanded = command;
              if (formattedCommanded.indexOf(",") > 0) {
                let splitCommand = formattedCommanded.split(",");
                formattedCommanded = splitCommand.join(", ");
              }
              return (
                <p key={index} className="_help-content__entry_ ">
                  {formattedCommanded}
                </p>
              );
            })}
          </div>
        </div>
      </TutorialPopover>
    </div>
  );
};
export default HelpMessage;
