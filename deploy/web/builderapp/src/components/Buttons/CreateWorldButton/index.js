/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* ICONS */
import { BsFillPlusCircleFill } from 'react-icons/bs';
//IconButton - 
const CreateWorldButton = ({ clickFunction }) => {
  return (
    <div className="createworldbutton-container" onClick={clickFunction}>
        <BsFillPlusCircleFill className="createworld-icon" />
        <p style={{ margin: 0, padding: "0 0 0 3px" }} className="createworldbutton-text">
           CREATE NEW 
        </p>
    </div>
  );
};

export default CreateWorldButton;