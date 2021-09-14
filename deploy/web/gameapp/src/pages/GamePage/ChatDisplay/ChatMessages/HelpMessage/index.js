/* REACT */
import React, { useState, useEffect } from "react";
/* STYLES */
import "./styles.css";
/* ICONS */
import { FaQuestion } from "react-icons/fa";
/* TOOLTIP */
import { Tooltip } from "react-tippy";

const HelpMessage = ({ text }) => {
  const [commandList, setCommandList] = useState([]);
  useEffect(() => {
    let commandArr = text.split("\n");
    commandArr = commandArr.slice(5, commandArr.length - 2);
    setCommandList(commandArr);
  }, [text]);

  // const TextArr = text.split("\n");
  // const Parchment = TextArr[4];
  // const CommandList = TextArr.slice(5, TextArr.length - 2);

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
