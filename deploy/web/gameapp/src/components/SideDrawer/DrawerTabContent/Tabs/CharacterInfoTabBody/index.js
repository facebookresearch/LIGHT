/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsXLg } from "react-icons/bs";

const CharacterInfoTabBody = ({ currentTab }) => {
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //PERSONA
  const characterName = useAppSelector((state) => state.persona.name);
  //PLAYER XP STATE
  const xp = useAppSelector((state) => state.xp.value);
  const level = useAppSelector((state) => state.xp.level);
  const xpToNextLevel = useAppSelector((state) => state.xp.xpToNextLevel);
  const progressPercent = useAppSelector((state) => state.xp.progressPercent);
  //GIFTXP STATE
  const giftXp = useAppSelector((state) => state.giftXp.value);
  /* REDUX ACTIONS */

  /* ------ LOCAL STATE ------ */
  const [mission, setMission] = useState("");
  const [items, setItems] = useState([]);

  useEffect(() => {}, [xp]);

  useEffect(() => {
    console.log(" SIDEBAR giftXP", giftXp);
  }, [giftXp]);
  return (
    <div className="">
      <h5 className="__sidedrawer-level-label__ font-bold">Level</h5>
      <p className="__sidedrawer-level-value__ ">{level}</p>
      <h5 className="__sidedrawer-totalxp-label__ font-bold">Total XP</h5>
      <p className="__sidedrawer-totalxp-value__ ">{xp}</p>
      <h5 className="__sidedrawer-role-label__ font-bold">Role</h5>
      <p className="__sidedrawer-role-value__ ">
        {characterName.toUpperCase()}
      </p>
      <h5 className="__sidedrawer-mission-label__ font-bold">Mission</h5>
      <p className="__sidedrawer-mission-value ">{mission}</p>
      <h5>Items</h5>
      <p></p>
    </div>
  );
};

export default CharacterInfoTabBody;
