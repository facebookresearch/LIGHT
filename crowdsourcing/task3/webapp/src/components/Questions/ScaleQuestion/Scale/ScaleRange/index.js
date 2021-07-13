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
        <div className="scalerange-keys">
            <div className="scalerange-key__container" style={{backgroundColor:"green", borderBottomLeftRadius:"15px"}}>
                <p className="scalerange-key__text" >
                    MIN
                </p>
            </div>
            <div className="scalerange-key__container" style={{backgroundColor:"blue"}}>
                <p className="scalerange-key__text">
                    MID
                </p>
            </div>
            <div className="scalerange-key__container" style={{backgroundColor:"red"}} >
                <p className="scalerange-key__text">
                    MAX
                </p>
            </div>
        </div>
    </div>
  );
};

export default ScaleRange;
