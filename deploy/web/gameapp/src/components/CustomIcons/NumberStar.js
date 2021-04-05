import React from "react";
import "./styles.css";
import { FaStar } from "react-icons/fa";

const NumberStar = (props) => {
  const { number, iconStyle } = props;
  return (
    <div className="customicon">
      <FaStar size="10em" style={iconStyle} />
      <div className="customicon-text__container">
        <h3 className="customicon-text">Gift EXP </h3>
        <h1 className="customicon-text">{number} </h1>
      </div>
    </div>
  );
};

export default NumberStar;
