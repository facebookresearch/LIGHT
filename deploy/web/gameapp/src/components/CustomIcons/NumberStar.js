import React from "react";
import "./styles.css";
import { FaStar } from "react-icons/fa";

const NumberStar = (props) => {
  const { number, iconStyle, size } = props;

  return (
    <div className="customicon">
      <FaStar size={size} style={iconStyle} />
      <div className="customicon-text__container">
        <h5 className="customicon-text">Gift EXP </h5>
        <h5 className="customicon-text">{number} </h5>
      </div>
    </div>
  );
};

export default NumberStar;
