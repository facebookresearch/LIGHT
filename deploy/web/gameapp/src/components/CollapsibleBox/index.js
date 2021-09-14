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
  collapsedContent,
  children,
}) => {
  /* ----LOCAL STATE---- */
  const [isCollapsed, setIsCollapsed] = useState(false);
  const openHandler = () => setIsCollapsed(false);
  const closeHandler = () => setIsCollapsed(true);

  return (
    <div className="collapsible-container">
      <div
        className="collapsible-header"
        style={{
          backgroundColor: titleBg,
          borderRadius: isCollapsed ? "15px" : null,
        }}
      >
        <div />
        <h3 className="collapsible-header--text">{title}</h3>
        <div className="collapsible-header--icon">
          {isCollapsed ? (
            <BiWindow color="black" onClick={openHandler} />
          ) : (
            <FaWindowMinimize color="black" onClick={closeHandler} />
          )}
        </div>
      </div>
      {isCollapsed ? (
        <div>{collapsedContent}</div>
      ) : (
        <div
          className="collapsible-body"
          style={{ backgroundColor: containerBg }}
        >
          {children}
        </div>
      )}
    </div>
  );
};

export default CollapsibleBox;
