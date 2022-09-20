/* REACT */
import React, { useState } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
/* STYLES */
import "./styles.css";
//CUSTOM COMPONENTS
import GameButton from "../../../../GameButton";
/* ICONS */
import { BsXLg } from "react-icons/bs";

const SystemTabBody = ({ currentTab }) => {
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //PERSONA
  const persona = useAppSelector((state) => state.persona);
  /* REDUX ACTIONS */

  /* ------ LOCAL STATE ------ */

  return (
    <div className="">
      <a href={"/logout"} style={{ color: "#0060B6", textDecoration: "none" }}>
        <GameButton text={"LOGOUT"} clickFunction={() => {}} />
      </a>
    </div>
  );
};

export default SystemTabBody;
