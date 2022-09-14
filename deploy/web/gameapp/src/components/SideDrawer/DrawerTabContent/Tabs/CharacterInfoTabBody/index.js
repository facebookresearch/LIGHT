/* REACT */
import React, { useState } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { updateShowDrawer } from "../../features/view/view-slice";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsXLg } from "react-icons/bs";

const CharacterInfoTabBody = ({ currentTab }) => {
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //PERSONA
  const persona = useAppSelector((state) => state.persona);
  /* REDUX ACTIONS */

  /* ------ LOCAL STATE ------ */

  return <div className=""></div>;
};

export default CharacterInfoTabBody;
