
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* CUSTOM COMPONENTS */
import TutorialImageLg from "../../../components/TutorialImages/TutorialImageLg";
import TutorialImageSm from "../../../components/TutorialImages/TutorialImageSm";
/* COPY */
import PreviewCopy from "../../../PreviewCopy"

//PreviewContent -  Content that be viewed in both Preview view and Task Container
const PreviewContent = () => {
    const {intro, uiSteps, chatSteps, reportSteps} = PreviewCopy
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
            {
              reportSteps.map((step, index)=>(
                <TutorialImageLg key={index} info ={step} />
              ))
            }
        </div>
    )
};

export default PreviewContent;
