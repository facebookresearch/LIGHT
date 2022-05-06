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
