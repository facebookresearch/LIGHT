/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsCircleFill } from "react-icons/bs";

//NumberCircle - Renders number at center of custom styled circle
const NumberCircle = ({ number }) => {
  return (
    <div className="numbercircle-container">
      <div className="circle-container">
        <BsCircleFill className="level-circle" />
      </div>
      <div className="numbercircle-text__container">
        <p className="numbercircle-text">LVL {"\n" + number}</p>
      </div>
    </div>
  );
};

export default NumberCircle;
