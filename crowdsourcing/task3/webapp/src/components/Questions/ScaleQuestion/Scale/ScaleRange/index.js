//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"
//CUSTOM COMPONENTS

const ScaleRange = ({
    scale
}) => {

  return (
    <div className="scalerange-container">
        <div className="optionblock-footer"></div>
        <div className="scalerange-keys__container">
            <p className="scalerange-keys__text" >
                MIN
            </p>
            <p className="scalerange-keys__text">
                MID
            </p>
            <p className="scalerange-keys__text">
                MAX
            </p>
        </div>
    </div>
  );
};

export default ScaleRange;
