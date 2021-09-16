/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsInfo } from "react-icons/bs";

//IconButton - Renders button that toggles help mode.
const IconButton = ({ buttonFunction, active }) => {
  return (
    <BsInfo
      className={`iconbutton ${active ? "active" : ""} `}
      onClick={buttonFunction}
    />
  );
};

export default IconButton;
