/* REACT */
import React, { useState } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { updateShowDrawer } from "../../features/view/view-slice";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsXLg } from "react-icons/bs";

// Modal - generates modal frame with overlay
const SideDrawer = () => {
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //PERSONA
  const persona = useAppSelector((state) => state.persona);
  /* REDUX ACTIONS */
  const closeDrawer = () => {
    dispatch(updateShowDrawer(false));
  };
  /* ------ LOCAL STATE ------ */
  const [selectedTab, setSelectedTab] = useState("character-info");
  const TabSelectionHandler = (tabVal) => {
    setSelectedTab(tabVal);
  };
  return (
    <div className="sidedrawer w-full">
      <div className="__sidedrawer-header__ w-full flex justify-end p-1">
        <BsXLg onClick={closeDrawer} />
      </div>
      <div className="__sidedrawer-header__ flex justify-center items-center">
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
            className={`tab ${selectedTab === "system" ? "tab-active" : ""}`}
            onClick={() => TabSelectionHandler("system")}
          >
            System
          </a>
          {/* <a
            className={`tab ${selectedTab === "rewards" ? "tab-active" : ""}`}
            onClick={() => TabSelectionHandler("rewards")}
          >
            Rewards
          </a> */}
        </div>
      </div>
      <div></div>
    </div>
  );
};

export default SideDrawer;
