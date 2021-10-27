/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//GameButton - renders theme styled button that will perform function passed as props and be labeled with text passed as props
const GameButton = ({ clickFunction, text }) => {
  return (
    <div className="button-container" onClick={clickFunction}>
      <p style={{ margin: 0, padding: 0 }} className="button-text">
        {text}
      </p>
    </div>
  );
};

export default GameButton;
