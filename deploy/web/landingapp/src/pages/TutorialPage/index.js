import React from "react";
import { Link } from "react-router-dom";

//Topics
import HowToPlay from "./Topics/HowToPlay";
import ExperiencePointsSystem from "./Topics/ExperiencePointsSystem";
import CharacterBasics from "./Topics/CharacterBasics";
import InteractingWithTheWorld from "./Topics/InteractingWithTheWorld";
import Actions from "./Topics/Actions";
//IMAGES
import Scribe from "../../assets/images/scribe.png";

import "./styles.css";

const TutorialPage = (props) => {
  return (
    <div className="tutorialpage-container">
      <div className="tutorialpage-content">
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
