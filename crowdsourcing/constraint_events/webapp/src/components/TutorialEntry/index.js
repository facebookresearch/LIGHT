import React, {useEffect, useState, useRef} from "react";

import "./styles.css"


const TutorialEntry = ({
    question,
    explanation,
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
                    {explanation}
                </p>
            </div>
            <div className="tutorialentry-img">
                {screenshot ? <img style={{width:"50%"}} src={screenshot} />: null}
            </div>
        </div>
    )
}
export default TutorialEntry;
