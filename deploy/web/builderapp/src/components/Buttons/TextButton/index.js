/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//TextButton - 
const TextButton = ({ clickFunction, text }) => {
  return (
    <div className="textbutton-container" onClick={clickFunction}>
      <p style={{ margin: 0, padding: 0 }} className="textbutton-text">
        {text}
      </p>
    </div>
  );
};

export default TextButton;