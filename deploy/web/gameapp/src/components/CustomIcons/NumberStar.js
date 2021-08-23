import React from "react";
import "./styles.css";
import { FaStar } from "react-icons/fa";

const NumberStar = (props) => {
  const { number, iconStyle, size } = props;

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
