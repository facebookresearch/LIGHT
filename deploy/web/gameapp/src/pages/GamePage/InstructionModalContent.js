import React, { useState, useEffect } from "react";

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
          Welcome to <span>LIGHT</span>
        </h1>
      </div>
    </div>
  );
};

export default InstructionModalContent;
