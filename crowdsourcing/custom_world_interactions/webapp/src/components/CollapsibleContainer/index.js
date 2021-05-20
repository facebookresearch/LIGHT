import React, { useState, useEffect } from "react";

import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";

import "./styles.css";

const CollapsibleBox = (props) => {
  const { title, titleBg, containerBg, collapsedContent } = props;

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
          {props.children}
        </div>
      )}
    </div>
  );
};

export default CollapsibleBox;
