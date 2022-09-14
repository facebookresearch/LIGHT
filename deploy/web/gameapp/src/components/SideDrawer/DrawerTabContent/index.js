/* REACT */
import React, { useState } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { updateShowDrawer } from "../../features/view/view-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import CharacterInfoTabBody from "./Tabs/CharacterInfoTabBody";
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

  const TabContent = () => {
    switch (currentTab) {
      case "character-info":
        return <CharacterInfoTabBody />;
      case "system":
        break;
      default:
        return <CharacterInfoTabBody />;
    }
  };
  return (
    <div className="sidedrawer w-full">
      <TabContent />
    </div>
  );
};

export default SideDrawer;
