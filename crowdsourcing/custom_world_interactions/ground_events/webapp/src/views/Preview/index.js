//REACT
import React from "react";
//STYLES
import "./styles.css"
//COPY
import Copy from "../../TaskCopy"
const PreviewTutorial = Copy.tutorialIntro.explanation;
const PreviewTutorialImg= Copy.tutorialIntro.screenshot;
const EventTutorialIntro = Copy.event.tutorialIntro;
const EventTutorial = Copy.event.tutorialCopy;
//Custom Components
import TutorialEntry from "../../components/TutorialEntry"
import Header from "../../components/Header";

//Preview - Renders the Task Preview with tutorial components and entries.
const Preview = ({}) => {
    return (
      <div className="view-container">
        <Header />
        <div className="intro-container">
          <img src={PreviewTutorialImg} style={{width:"100%"}} />
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
                  if (index >= 5) {
                    return <div />
                  }
                  const {question, explanation, screenshot} = entry;
                  return <TutorialEntry key={index} question={question} explanation={explanation} screenshot={screenshot}/>
                })
              }
            </div>
          </div>
        </div>
      </div>
    );
}

export default Preview ;
