
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//STYLES
import "./styles.css";
//CUSTOM COMPONENTS
import TutorialEntry from "../../components/TutorialEntry"
import Header from "../../components/Header";
//COPY
import Copy from "../../TaskCopy"
const {previewCopy, taskHeader} = Copy;
const {tutorial} = previewCopy;
const {intro, questionsCopy}= tutorial;

//Preview - component renders the Task Preview with tutorial components and entries.
const Preview = ({}) => {
    return (
      <div className="preview-container">
        <Header
          headerText={taskHeader}
        />
        <div className="intro-container">
          <div className="intro-header__container">
            <h1 className="intro-header__text">
              Task Instructions
            </h1>
          </div>
          <div className="intro-body__container">
            <p className="intro-body__text">
              {intro}
            </p>
          </div>
        </div>
        {questionsCopy.map(({questionName, steps}, index)=>{
          return (
            <div className="section-container">
              <TutorialEntry
                key={questionName}
                question={questionName}
                explanation=""
              >
                {
                  steps.map((step, index)=>{
                    const {stepCopy, stepImg} = step;
                    return (
                      <TutorialEntry
                        key={index}
                        explanation={stepCopy}
                        screenshot={stepImg}
                      />
                    )
                  })
                }
              </TutorialEntry>
            </div>
          )
        })}
      </div>
    );
}

export default Preview ;
