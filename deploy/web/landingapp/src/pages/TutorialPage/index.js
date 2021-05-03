import React from "react";
import { Link } from "react-router-dom";

//Topics
import HowToPlay from "./Topics/HowToPlay";
import ExperiencePointsSystem from "./Topics/ExperiencePointsSystem";
import CharacterBasics from "./Topics/CharacterBasics";
import InteractingWithTheWorld from "./Topics/InteractingWithTheWorld";
import Actions from "./Topics/Actions";

import "./styles.css";

const TutorialPage = (props) => {
  return (
    <div className="tutorialpage-container">
      <HowToPlay />
      <ExperiencePointsSystem />
      <CharacterBasics />
      <InteractingWithTheWorld />
      <Actions />
    </div>
  );
};

export default TutorialPage;
