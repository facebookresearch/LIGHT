import React, {useEffect, useState, useRef} from "react";

import "./styles.css"


const TutorialEntry = ({
    question,
    explaination,
    screenshot,
})=>{
    return(
        <div className="tutorialentry-container">
            <div className="tutorialentry-header">
                <p className="tutorialentry-header__text">
                    {question}
                </p>
            </div>
            <div className="tutorialentry-body">
                <p className="tutorialentry-body__text">
                    {explaination}
                </p>
            </div>
            <div className="tutorialentry-img">

            </div>
        </div>
    )
}
export default TutorialEntry;
