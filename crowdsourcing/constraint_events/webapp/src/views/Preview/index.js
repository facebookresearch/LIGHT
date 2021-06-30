import React, { useEffect } from "react";
//STYLES
import "./styles.css"
//COPY
import Copy from "../../TaskCopy"
const PreviewTutorial = Copy.tutorialIntro.explanation;
const PreviewTutorialImg= Copy.tutorialIntro.screenshot;
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
          <img src={PreviewTutorialImg} style={{width:"50%"}} />
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
                  const {question, explanation, screenshot} = entry;
                  return <TutorialEntry key={index} question={question} explanation={explanation} screenshot={screenshot}/>
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
                    const {question, explanation, screenshot} = entry;
                    return <TutorialEntry key={index} question={question} explanation={explanation} screenshot={screenshot} />
                  })
                }
              </div>
          </div>
        </div>
      </div>
    );
}

export default Preview ;
