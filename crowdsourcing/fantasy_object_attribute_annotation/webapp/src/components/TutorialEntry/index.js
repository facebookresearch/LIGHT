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
            {children}
        </div>
    )
}
export default TutorialEntry;
