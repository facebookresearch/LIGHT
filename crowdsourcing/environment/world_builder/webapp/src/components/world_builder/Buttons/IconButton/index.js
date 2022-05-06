/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//IconButton -
const IconButton = ({ clickFunction, text }) => {
  return (
    <div className="iconbutton-container" onClick={clickFunction}>

    </div>
  );
};

export default IconButton;
