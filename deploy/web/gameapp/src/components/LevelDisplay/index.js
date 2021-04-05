import React, { useState, useEffect } from "react";

import "./styles.css";

import ProgressBar from "../Progressbar";

const LevelDisplay = (props) => {
  const { experience } = props;
  const [level, setLevel] = useState(1);
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
    setExp(currentExp);
    setProgressPercent(percent);
  };
  useEffect(() => {
    levelCalculator();
  }, []);
  return (
    <div className="leveldisplay-container">
      <div className="level-container">
        <h3 className="level-number">{`LVL ${level}`}</h3>
      </div>
      <ProgressBar
        bgcolor={"yellow"}
        percentCompleted={progressPercent}
        exp={exp}
      />
    </div>
  );
};

export default LevelDisplay;
