import React, { useState, useEffect } from "react";

import { Tooltip } from "react-tippy";

import "./styles.css";

import ProgressBar from "../ProgressBar";
import LevelDisplay from "../LevelDisplay";

const ExperienceInfo = (props) => {
  const { experience } = props;
  const [level, setLevel] = useState(1);
  const [neededExp, setNeededExp] = useState(0);
  const [exp, setExp] = useState(0);
  const [giftExp, setGiftExp] = useState(3);
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
  }, []);
  return (
    <div className="experienceinfo-container">
      <LevelDisplay level={level} giftExp={giftExp} />
      <div style={{ width: "100%", marginLeft: "10%", marginRight: 0 }}>
        <Tooltip title={`Earn ${neededExp}XP to level up`} position="top">
          <ProgressBar
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
