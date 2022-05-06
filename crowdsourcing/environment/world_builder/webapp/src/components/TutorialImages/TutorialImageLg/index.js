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
