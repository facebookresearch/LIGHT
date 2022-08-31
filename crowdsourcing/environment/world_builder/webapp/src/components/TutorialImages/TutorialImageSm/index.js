
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css"

const TutorialImageSm = ({
    info
})=>{
    const {image, text} = info;
    return(
        <div className="tutorial-container__sm">
            <div className="smtutorial-image__container" >
                <img className="smtutorial-image" src={image} />
            </div>
            <div className="smtutorial-text__container" >
                <p className="smtutorial-text" >{text}</p>
            </div>
        </div>
    )
}

export default TutorialImageSm;
