
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//STYLING
import "./styles.css"

//ScaleRange - Generates range for flags from scaleRange array producing a section for each object in array with associated label and color
const ScaleFooter = ({
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
                        <div key={index} className="scalerange-key__container" style={{width:(rangeWidth+"%"), backgroundColor:color, borderBottomLeftRadius:index==0 ? "15px" : 0}}>
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

export default ScaleFooter;
