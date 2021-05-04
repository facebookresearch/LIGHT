import React, { useState, useEffect } from "react";
import { Link } from "react-dom";

import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";
//IMAGES
import Scribe from "../../assets/images/scribe.png";

import "./styles.css";

const InstructionModalContent = (props) => {
  return (
    <div className="instructionmodalcontent-container">
      <div className="instructionmodalcontent-header">
        <img className="instructionmodalcontent-image" src={Scribe} />
        <h1>
          Playing <span>LIGHT</span>
        </h1>
      </div>
      <div className="instructionmodalcontent-body">
        <p className="instructionmodalcontent-body__text">
          The LIGHT interface attempts to interpret anything typed into it as an
          action.
        </p>
        <p className="instructionmodalcontent-body__text">
          To speak, you should wrap your sentence in quotes, or use shift+enter
          to send your messages.
        </p>
        <p className="instructionmodalcontent-body__text">
          A list of commands can be displayed with "help" and you can find a
          more complete list of instructions
          <a href={"/#/tutorial"}>here </a>
        </p>
      </div>
    </div>
  );
};

export default InstructionModalContent;
