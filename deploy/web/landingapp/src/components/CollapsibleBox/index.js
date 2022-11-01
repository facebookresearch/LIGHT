/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState } from "react";
/* ICONS */
import { BsPlusLg } from "react-icons/bs";
import { FaWindowMinimize } from "react-icons/fa";
/* STYLES */
import "./styles.css";

// CollapsibleBox - renders collapsible container with customizable colors, header, and hides children upon "collapse"
const CollapsibleBox = ({
  title,
  collapsedContent,
  children,
  onClickFunction,
}) => {
  /* ----LOCAL STATE---- */
  const [isCollapsed, setIsCollapsed] = useState(false);
  /* ----HANDLERS---- */
  //openHandler - Shows contents of container
  const openHandler = () => setIsCollapsed(false);
  //closeHandler - Hides contents of container
  const closeHandler = () => setIsCollapsed(true);

  return (
    <div className={`collapsible-container `} onClick={onClickFunction}>
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
            <BsPlusLg color="white" onClick={openHandler} />
          ) : (
            <FaWindowMinimize color="white" onClick={closeHandler} />
          )}
        </div>
      </div>
      {isCollapsed ? (
        <div>{collapsedContent}</div>
      ) : (
        <div className="collapsible-body">{children}</div>
      )}
    </div>
  );
};

export default CollapsibleBox;
