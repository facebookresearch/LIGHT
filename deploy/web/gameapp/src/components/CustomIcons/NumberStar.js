/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* ICONS */
import { FaStar } from "react-icons/fa";

//NumberStar - Renders number at center of custom styled star
const NumberStar = ({ number }) => {
  return (
    <div className="numberstar-container">
      <div className="star-container">
        <FaStar className="gift-star" />
      </div>
      <div className="numberstar-text__container">
        <h5 className="numberstar-text">{number} </h5>
      </div>
    </div>
  );
};

export default NumberStar;
