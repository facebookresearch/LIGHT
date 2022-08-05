/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppSelector } from "../../../../app/hooks";
//TOOLTIP
import { Tooltip } from "react-tippy";
//STYLES
//import "./styles.css";
//CUSTOM COMPONENTS
import LevelDisplay from "../../../../components/LevelDisplay";

/* IMAGES */
import Scribe from "../../../../assets/images/scribe.png";

//
const SidebarHeader = () => {
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
    <div>
      <div className="flex flex-row justify-start items-center">
        <img className="inline-block h-14 w-14 rounded-full" src={Scribe} />
        <div>
          <p style={{ color: "white" }}> {`You are level ${level}`} </p>
          <progress
            className="progress progress-success w-56 h-4 border-solid border-white border-2"
            value={progressPercent}
            max="100"
          ></progress>
        </div>
      </div>
      {/* <div className="experienceinfo-leveldisplay">
        <LevelDisplay level={level} giftExperience={Math.floor(giftXp)} />
      </div> */}
      {/* <div className="experienceinfo-progressbar">
        <Tooltip title={`Earn ${neededExp - exp}XP to level up`} position="top">
          {/* <Progressbar
            bgcolor={"yellow"}
            percentCompleted={progressPercent}
            exp={exp}
            nextLevel={neededExp}
          /> */}
      {/* </Tooltip> */}
      {/* </div> */}
    </div>
  );
};

export default SidebarHeader;
