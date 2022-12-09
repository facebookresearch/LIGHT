/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//Styling
import "./styles.css"

// Tutorial Entry - renders a formated entry for tutorial with relevant question, tutorial text, and screenshot
const TutorialEntry = ({
    question,//Question being explained
    explanation,//Explanation text
    screenshot,// Screenshot of question and UI
    children
})=>{
    return(
        <div className="tutorialentry-container">
            {
                question ?
                <div className="tutorialentry-header">
                    <p className="tutorialentry-header__text">
                        {question}
                    </p>
                </div>
                :
                null
            }
            {
                explanation ?
                <div className="tutorialentry-body">
                    <p className="tutorialentry-body__text">
                        {explanation}
                    </p>
                </div>
                :
                null
            }
            <div className="tutorialentry-img">
                {screenshot ? <img style={{width:"50%"}} src={screenshot} />: null}
            </div>
            {children}
        </div>
    )
}
export default TutorialEntry;
