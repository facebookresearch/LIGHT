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
import { GiConsoleController } from "react-icons/gi";

//
const SidebarHeader = () => {
  /* ----LOCAL STATE---- */
  //Character level
  const [level, setLevel] = useState(1);
  //Experience needed for next level
  const [neededExp, setNeededExp] = useState(0);
  //Percent of progress towards next level
  const [progressPercent, setProgressPercent] = useState(0);
  /* ----REDUX STATE---- */
  //PLAYER XP STATE
  const xp = useAppSelector((state) => state.xp.value);
  //SESSION XP STATE
  const sessionXp = useAppSelector((state) => state.sessionXp.value);
  //GIFTXP STATE
  const giftXp = useAppSelector((state) => state.giftXp.value);

  // UTIL
  const levelCalculator = () => {
    // BASE VALUES
    let currentLevel = 1;
    let currentExp = xp + sessionXp;
    let expToLevel = currentLevel * 10;
    // Level is calculated by subtracting total exp by required experience for each level
    while (expToLevel <= currentExp) {
      currentLevel++;
      currentExp -= expToLevel;
      expToLevel = currentLevel * 10;
    }
    let updatedPercent = Math.floor((currentExp / expToLevel) * 100);
    setLevel(currentLevel);
    setNeededExp(expToLevel);
    setProgressPercent(updatedPercent);
  };

  useEffect(() => {
    levelCalculator();
  }, [xp, sessionXp]);

  return (
    <div>
      <div className="flex flex-row justify-start items-center">
        <img className="inline-block h-14 w-14 rounded-full" src={Scribe} />
        <div>
          <p style={{ color: "white" }}> {`You are level ${level}`} </p>
          <Tooltip
            title={`Earn ${neededExp - sessionXp} XP til level ${level + 1}`}
            position="top"
          >
            <progress
              className="progress progress-warning w-full h-4 border-solid border-white border-2"
              value={progressPercent}
              max="100"
            />
          </Tooltip>
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
