/* REACT */
import React, { useState } from "react";
/* ICONS */
import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";
/* STYLES */
import "./styles.css";

// CollapsibleBox - renders collapsible container with customizable colors, header, and hides children upon "collapse"
const CollapsibleBox = ({
  title,
  titleBg,
  containerBg,
  children,
}) => {

  /* ----LOCAL STATE---- */

  return (
    <div
      className="collapsible-container"
      style={{backgroundColor: containerBg}}
    >
      <div
        className="collapsible-header"
        style={{
          backgroundColor: titleBg,

        }}
      >
        <div />
        <h3 className="collapsible-header--text">{title}</h3>
      </div>
        <div
          className="collapsible-body"
          style={{ backgroundColor: "#e0fffe" }}
        >
          {children}
        </div>
    </div>
  );
};

export default CollapsibleBox;
