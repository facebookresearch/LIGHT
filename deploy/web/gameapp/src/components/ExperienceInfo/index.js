/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppSelector } from "../../app/hooks";
//TOOLTIP
import { Tooltip } from "react-tippy";
//STYLES
import "./styles.css";
//CUSTOM COMPONENTS
import Progressbar from "../Progressbar";
import LevelDisplay from "../LevelDisplay";

// ExperienceInfo - component that calculates a players level and progress from their xp
//then renders the Level Display and Progress bar with those values
const ExperienceInfo = () => {
  /* ----LOCAL STATE---- */
  const [level, setLevel] = useState(1);
  const [neededExp, setNeededExp] = useState(0);
  const [exp, setExp] = useState(0);
  const [progressPercent, setProgressPercent] = useState(0);
  /* ----REDUX STATE---- */
  //XP
  const xp = useAppSelector((state) => state.xp.value);
  //GIFTXP
  const giftXp = useAppSelector((state) => state.giftXp.value);

  const levelCalculator = () => {
    let currentLevel = 1;
    let currentExp = xp;
    let expToLevel = currentLevel * 10;
    while (expToLevel <= currentExp) {
      currentLevel++;
      currentExp -= expToLevel;
      expToLevel = currentLevel * 10;
    }
    let nextLevel = currentLevel * 5 * (currentLevel + 1);
    let percent = Math.floor((xp / nextLevel) * 100);
    setLevel(currentLevel);
    setNeededExp(nextLevel);
    setExp(xp);
    setProgressPercent(percent);
  };

  useEffect(() => {
    levelCalculator();
  }, [xp]);
  return (
    <div className="experienceinfo-container">
      <div className="experienceinfo-leveldisplay">
        <LevelDisplay level={level} giftExperience={Math.floor(giftXp)} />
      </div>
      <div className="experienceinfo-progressbar">
        <Tooltip title={`Earn ${neededExp - exp}XP to level up`} position="top">
          <Progressbar
            bgcolor={"yellow"}
            percentCompleted={progressPercent}
            exp={exp}
            nextLevel={neededExp}
          />
        </Tooltip>
      </div>
    </div>
  );
};

export default ExperienceInfo;
