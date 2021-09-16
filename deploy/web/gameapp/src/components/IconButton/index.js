/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsInfo } from "react-icons/bs";

//IconButton - Renders button that toggles help mode.
const IconButton = ({ buttonFunction }) => {
  return <BsInfo className="iconbutton-icon" onClick={buttonFunction} />;
};

export default IconButton;
