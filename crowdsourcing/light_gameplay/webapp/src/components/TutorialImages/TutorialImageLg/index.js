
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css"

const TutorialImageLg = ({
    info
})=>{
    const {image, text} = info;
    return(
            <div className="tutorial-container__lg">
                <div className="lgtutorial-image__container">
                    <img className="lgtutorial-image" src={image} />
                </div>
                <div className="lgtutorial-text__container" >
                    <p className="lgtutorial-text" >{text}</p>
                </div>
            </div>
    )
}

export default TutorialImageLg;
