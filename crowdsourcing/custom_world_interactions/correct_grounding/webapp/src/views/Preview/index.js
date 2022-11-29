//REACT
import React from "react";
//STYLES
import "./styles.css"
//COPY
import Copy from "../../TaskCopy"
const PreviewTutorial = Copy.tutorialIntro.explanation;
const PreviewTutorialImg= Copy.tutorialIntro.screenshot;
//Custom Components
import TutorialEntry from "../../components/TutorialEntry"
import Header from "../../components/Header";

//Preview - Renders the Task Preview with tutorial components and entries.
const TutorialSection = ({name, copyObject}) => {
  return (
    <div className="eventpreview-container">
      <div className="eventpreview-header">
          <p>{name}</p>
      </div>
      <div className="eventpreview-body">
        {copyObject.tutorialIntro}
        {
          copyObject.tutorialCopy.map((entry, index)=>{
            if (index >= 6) {
              return <div />
            }
            const {question, explanation, screenshot} = entry;
            return <TutorialEntry key={index} question={question} explanation={explanation} screenshot={screenshot}/>
          })
        }
      </div>
    </div>
  );
}

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
          <TutorialSection name={"Interaction"} copyObject={Copy.interaction} />
          <TutorialSection name={"Narration"} copyObject={Copy.narration} />
          <TutorialSection name={"Objects"} copyObject={Copy.objects} />
          <TutorialSection name={"Attributes"} copyObject={Copy.attributes} />
        </div>
      </div>
    );
}

export default Preview ;
