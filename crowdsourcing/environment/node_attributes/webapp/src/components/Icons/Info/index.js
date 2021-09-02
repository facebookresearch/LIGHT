//REACT
import React from "react";
//STYLING
import "./styles.css";
// ICONS
import { BsInfoCircle } from "react-icons/bs";


// InfoIcon - renders an info icon
const InfoIcon = ({dark})=><BsInfoCircle className={dark? "info-icon__dark" :"info-icon"} />

export default InfoIcon ;
