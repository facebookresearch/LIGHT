import React from "react";
import "./styles.css";
import { BsCircleFill } from "react-icons/bs";

const NumberCircle = (props) => {
  const { number, size } = props;

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
