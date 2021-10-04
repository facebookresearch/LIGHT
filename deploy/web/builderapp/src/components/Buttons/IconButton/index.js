/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//IconButton - 
const IconButton = ({ clickFunction, text }) => {
  return (
    <div className="iconbutton-container" onClick={clickFunction}>
      <p style={{ margin: 0, padding: 0 }} className="iconbutton-text">
        {text}
      </p>
    </div>
  );
};

export default IconButton;