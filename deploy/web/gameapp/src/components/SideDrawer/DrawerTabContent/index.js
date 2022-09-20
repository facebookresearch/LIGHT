/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { updateShowDrawer } from "../../../features/view/view-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import CharacterInfoTabBody from "./Tabs/CharacterInfoTabBody";
import SystemTabBody from "./Tabs/SystemTabBody";
/* ICONS */
import { BsXLg } from "react-icons/bs";

// Modal - generates modal frame with overlay
const SideDrawer = ({ currentTab }) => {
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //PERSONA
  const persona = useAppSelector((state) => state.persona);
  /* REDUX ACTIONS */

  /* ------ LOCAL STATE ------ */
  const [selectedTab, setSelectedTab] = useState("");

  useEffect(() => {
    setSelectedTab(currentTab);
  }, [currentTab]);

  const TabContent = ({ tab }) => {
    switch (tab) {
      case "character-info":
        return <CharacterInfoTabBody />;
      case "system":
        return <SystemTabBody />;
      default:
        return <CharacterInfoTabBody />;
    }
  };

  return <TabContent tab={selectedTab} />;
};

export default SideDrawer;
