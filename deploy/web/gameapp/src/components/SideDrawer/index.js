/* REACT */
import React, { useState } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsXLg } from "react-icons/bs";

// Modal - generates modal frame with overlay
const SideDrawer = () => {
  /* ------ REDUX STATE ------ */
  //PERSONA
  const persona = useAppSelector((state) => state.persona);
  /* ------ LOCAL STATE ------ */
  const [selectedTab, setSelectedTab] = useState("character-info");
  const TabSelectionHandler = (tabVal) => {
    setSelectedTab(tabVal);
  };
  return (
    <div className="sidedrawer w-1/4">
      <div></div>
      <div className="__sidedrawer-header__">
        <h1>MENU</h1>
      </div>
      <div className=""></div>
      <div className="">
        <div className="tabs tabs-boxed">
          <a
            className={`tab ${
              selectedTab === "character-info" ? "tab-active" : ""
            }`}
            onClick={() => TabSelectionHandler("character-info")}
          >
            Character Info
          </a>
          <a
            className={`tab ${selectedTab === "rewards" ? "tab-active" : ""}`}
            onClick={() => TabSelectionHandler("rewards")}
          >
            Rewards
          </a>
          <a className="tab">Tab 3</a>
        </div>
      </div>
      <div></div>
    </div>
  );
};

export default SideDrawer;
