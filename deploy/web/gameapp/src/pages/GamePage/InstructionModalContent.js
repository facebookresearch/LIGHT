import React, { useState, useEffect } from "react";
import { Link } from "react-dom";

import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";
//IMAGES
import Scribe from "../../assets/images/scribe.png";
import ActionText1 from "../../assets/screenshots/Tutorial/Interacting/Emote1.png";
import ActionText2 from "../../assets/screenshots/Tutorial/Interacting/Emote2.png";
import WrappedText from "../../assets/screenshots/Tutorial/Interacting/InteractingRespond.png";

import "./styles.css";

const InstructionModalContent = (props) => {
  return (
    <div className="instructionmodalcontent-container">
      <div className="instructionmodalcontent-header">
        <img className="instructionmodalcontent-scribe" src={Scribe} />
        <h1 className="instructionmodalcontent-header__text">
          Playing{" "}
          <span className="instructionmodalcontent-header__light">LIGHT</span>
        </h1>
      </div>
      <div className="instructionmodalcontent-body">
        <p className="instructionmodalcontent-body__text">
          The LIGHT interface attempts to interpret anything typed into it as an
          action.
        </p>
        <img className="instructionmodalcontent-image" src={ActionText1} />
        <p className="instructionmodalcontent-body__text">
          To speak, you should wrap your sentence in quotes, or use shift+enter
          to send your messages.
        </p>
        <img className="instructionmodalcontent-image" src={WrappedText} />
        <p className="instructionmodalcontent-body__text">
          A list of commands can be displayed with "help" and you can find a
          more complete list of instructions{" "}
          <a style={{ color: "white" }} href={"/#/tutorial"}>
            here
          </a>
          .
        </p>
      </div>
      <div className="instructionmodalcontent-row">
        <div className="instructionmodalcontent-button">READY</div>
      </div>
    </div>
  );
};

export default InstructionModalContent;
