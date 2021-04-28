import React, { useState, useEffect } from "react";

import { Tooltip } from "react-tippy";

import "./styles.css";

import Progressbar from "../Progressbar";
import LevelDisplay from "../LevelDisplay";

const ExperienceInfo = ({ experience, giftExperience }) => {
  const [level, setLevel] = useState(1);
  const [neededExp, setNeededExp] = useState(0);
  const [exp, setExp] = useState(0);
  const [progressPercent, setProgressPercent] = useState(0);

  const levelCalculator = () => {
    let currentLevel = 1;
    let currentExp = experience;
    let expToLevel = currentLevel * 10;
    while (expToLevel <= currentExp) {
      currentLevel++;
      currentExp -= expToLevel;
      expToLevel = currentLevel * 10;
    }
    let percent = Math.floor((currentExp / expToLevel) * 100);
    setLevel(currentLevel);
    setNeededExp(expToLevel - currentExp);
    setExp(currentExp);
    setProgressPercent(percent);
  };
  useEffect(() => {
    levelCalculator();
  }, [experience]);
  return (
    <div className="experienceinfo-container">
      <LevelDisplay level={level} giftExperience={Math.floor(giftExperience)} />
      <div style={{ width: "100%", marginLeft: "10%", marginRight: 0 }}>
        <Tooltip title={`Earn ${neededExp}XP to level up`} position="top">
          <Progressbar
            bgcolor={"yellow"}
            percentCompleted={progressPercent}
            exp={exp}
          />
        </Tooltip>
      </div>
    </div>
  );
};

export default ExperienceInfo;
