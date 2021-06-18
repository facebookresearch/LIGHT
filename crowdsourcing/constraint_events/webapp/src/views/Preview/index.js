import React, { useEffect } from "react";
//STYLES
import "./styles.css"
//COPY
import Copy from "../../TaskCopy"
const PreviewTutorial = Copy.tutorialIntro;
const EventTutorialIntro = Copy.event.tutorialIntro;
const ConstraintTutorialIntro = Copy.constraint.tutorialIntro;
const EventTutorial = Copy.event.tutorialCopy;
const ConstraintTutorial = Copy.constraint.tutorialCopy;


//Custom Components
import TutorialEntry from "../../components/TutorialEntry"
import Header from "../../components/Header";




const Preview = ({}) => {
    return (
      <div className="view-container">
        <Header />
        <div className="intro-container">
          <p className="intro-text">
            {PreviewTutorial}
          </p>
        </div>
        <div className="preview-container">
          <div className="eventpreview-container">
            <div className="eventpreview-header">
                <p>EVENTS</p>
            </div>
            <div className="eventpreview-body">
              {EventTutorialIntro}
              {
                EventTutorial.map((entry, index)=>{
                  const {question, explaination} = entry;
                  return <TutorialEntry key={index} question={question} explaination={explaination} />
                })
              }
            </div>
          </div>
          <div className="constraintpreview-container">
            <div className="constraintpreview-header">
                <p>CONSTRAINTS</p>
            </div>
              <div className="constraintpreview-body">
                {ConstraintTutorialIntro}
                {
                  ConstraintTutorial.map((entry, index)=>{
                    const {question, explaination} = entry;
                    return <TutorialEntry key={index} question={question} explaination={explaination} />
                  })
                }
              </div>
          </div>
        </div>
      </div>
    );
}

export default Preview ;
