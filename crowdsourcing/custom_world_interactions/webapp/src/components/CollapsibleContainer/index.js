import React, { useState, useEffect } from "react";

import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";

import "./styles.css";

const CollapsibleBox = ({ title, titleBg, containerBg, collapsedContent, children }) => {

  const [isCollapsed, setIsCollapsed] = useState(true);
  const openHandler = () => setIsCollapsed(false);
  const closeHandler = () => setIsCollapsed(true);

  return (
    <div className="collapsible-container">
      <div
        className="collapsible-header"
        style={{
          borderRadius: isCollapsed ? "15px" : null,
        }}
      >
        <div />
        <h3 className="collapsible-header--text">{title}</h3>
        <div className="collapsible-header--icon">
          {isCollapsed ? (
            <BiWindow color="white" onClick={openHandler} />
          ) : (
            <FaWindowMinimize color="white" onClick={closeHandler} />
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
