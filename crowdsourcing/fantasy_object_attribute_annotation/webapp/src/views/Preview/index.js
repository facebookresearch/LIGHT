//REACT
import React from "react";
//STYLES
import "./styles.css";
//Custom Components
import TutorialEntry from "../../components/TutorialEntry"
import Header from "../../components/Header";
//COPY
import Copy from "../../TaskCopy"
const {previewCopy} = Copy;
const {tutorial} = previewCopy;
const {questionsCopy}= tutorial

//Preview - Renders the Task Preview with tutorial components and entries.
const Preview = ({}) => {
    return (
      <div className="preview-container">
        <Header />
        {questionsCopy.map(({questionName, steps}, index)=>{
          return (
            <>
              <TutorialEntry
                key={index}
                question={questionName}
                explanation=""
              >
                {
                  steps.map((step, index)=>{
                    const {stepCopy, stepImg} = step
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
            </>
          )
        })}
      </div>
    );
}

export default Preview ;
