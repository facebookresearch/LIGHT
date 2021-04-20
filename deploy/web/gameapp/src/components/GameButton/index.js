import React, { useState, useEffect } from "react";

import "./styles.css";

const GameButton = ({ clickFunction, text }) => {
  return (
    <div className="button-container" onClick={clickFunction}>
      <p className="button-text">{text}</p>
    </div>
  );
};

export default GameButton;
