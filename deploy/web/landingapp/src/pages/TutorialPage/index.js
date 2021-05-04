import React from "react";
import { Link, useHistory } from "react-router-dom";

//Topics
import HowToPlay from "./Topics/HowToPlay";
import ExperiencePointsSystem from "./Topics/ExperiencePointsSystem";
import CharacterBasics from "./Topics/CharacterBasics";
import InteractingWithTheWorld from "./Topics/InteractingWithTheWorld";
import Actions from "./Topics/Actions";

import "./styles.css";

const TutorialPage = (props) => {
  let history = useHistory();
  return (
    <div className="tutorialpage-container">
      <div className="tutorialpage-content">
        <div style={{ width: "100%", display: "flex" }}>
          <div className="tutorialpage-button" onClick={() => history.goBack()}>
            Back
          </div>
        </div>
        <HowToPlay />
        <ExperiencePointsSystem />
        <CharacterBasics />
        <InteractingWithTheWorld />
        <Actions />
      </div>
    </div>
  );
};

export default TutorialPage;
