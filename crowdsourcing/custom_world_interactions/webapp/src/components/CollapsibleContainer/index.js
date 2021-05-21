import React, { useState, useEffect } from "react";


import "./styles.css";

const CollapsibleBox = (props) => {
  const { title, titleBg, containerBg, collapsedContent, children } = props;

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
            <i className="bi bi-window" onClick={openHandler} />
          ) : (
            <i className="bi bi-dash" onClick={closeHandler} />
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
