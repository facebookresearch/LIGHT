//REACT
import React, {useState} from "react";
//STYLING
import "./styles.css"

//ScaleRange - Generates range for flags from scaleRange array producing a section for each object in array with associated label and color
const ScaleRange = ({
    scaleRange
}) => {
  return (
    <div className="scalerange-container">
        <div className="optionblock-footer"></div>
        <div className="scalerange-keys">
            {
                scaleRange.length
                ?
                scaleRange.map((range, index)=>{
                    const {name, color} =range;
                    let rangeWidth = 100/scaleRange.length
                    return (
                        <div key={index} className="scalerange-key__container" style={{width:rangeWidth, backgroundColor:color, borderBottomLeftRadius:index==0 ? "15px" : 0}}>
                            <p className="scalerange-key__text" >
                                {name}
                            </p>
                        </div>
                    )
                })
                :
                null
            }
        </div>
    </div>
  );
};

export default ScaleRange;
