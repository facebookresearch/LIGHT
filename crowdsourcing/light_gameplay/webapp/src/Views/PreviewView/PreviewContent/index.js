/* REACT */
import React from "react";
/* CUSTOM COMPONENTS */
import TutorialImageLg from "../../../components/TutorialImages/TutorialImageLg";
import TutorialImageSm from "../../../components/TutorialImages/TutorialImageSm";
/* COPY */
import PreviewCopy from "../../../PreviewCopy"

//PreviewContent -  Content that be viewed in both Preview view and Task Container
const PreviewContent = () => {
    const {intro, uiSteps, chatSteps} = PreviewCopy
    return (
        <div className="previewinfo-body">
            <p className="previewinfo-intro">
              {intro}
            </p>
            {
              uiSteps.map((step, index)=>(
                <TutorialImageSm key={index} info ={step} />
              ))
            }
            {
              chatSteps.map((step, index)=>(
                <TutorialImageLg key={index} info ={step} />
              ))
            }
        </div>
    )
};

export default PreviewContent;
