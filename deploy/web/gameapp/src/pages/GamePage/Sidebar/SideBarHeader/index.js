/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
/* ---- REDUCER ACTIONS ---- */
import { useAppSelector, useAppDispatch } from "../../../../app/hooks";
import { updateShowDrawer } from "../../../../features/view/view-slice";
import { updateSelectedTip } from "../../../../features/tutorials/tutorials-slice";
//TOOLTIP
import { Tooltip } from "react-tippy";
//STYLES
//import "./styles.css";
//CUSTOM COMPONENTS
import LevelDisplay from "../../../../components/LevelDisplay";
import GameButton from "../../../../components/GameButton";
import IconButton from "../../../../components/IconButtons/InfoButton";
import ToggleSwitch from "../../../../components/ToggleSwitch";
/* IMAGES */
import Scribe from "../../../../assets/images/scribe.png";
import { GiConsoleController } from "react-icons/gi";

//
const SidebarHeader = () => {
  const dispatch = useAppDispatch();
  /* REDUX STATE */
  //DRAWER
  const showDrawer = useAppSelector((state) => state.view.showDrawer);
  /* REDUX ACTIONS */
  const openDrawer = () => {
    dispatch(updateShowDrawer(true));
  };
  const closeDrawer = () => {
    dispatch(updateShowDrawer(false));
  };
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
    setNeededExp(expToLevel - currentExp);
    setProgressPercent(updatedPercent);
  };

  useEffect(() => {
    levelCalculator();
  }, [xp, sessionXp]);

  return (
    <>
      <div className="flex flex-row justify-start items-center w-full">
        <div className="flex flex-row justify-start items-center w-1/2">
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
        <div className="w-1/2 flex flex-row justify-around">
          <div className="flex flex-row justify-center items-center">
            <IconButton />
          </div>
          <div className="flex flex-row justify-center items-center">
            <a
              href={"/logout"}
              style={{ color: "#0060B6", textDecoration: "none" }}
            >
              <GameButton text={"LOGOUT"} clickFunction={() => {}} />
            </a>
            {/* <div>
          <ToggleSwitch
            switchLabel="CHARACTER INFO"
            toolTipText={
              showDrawer
                ? "Click to return to the game"
                : "Click to open your character info."
            }
            isOn={showDrawer}
            setOn={openDrawer}
            setOff={closeDrawer}
          />
        </div> */}
          </div>
        </div>
      </div>
    </>
  );
};

export default SidebarHeader;
