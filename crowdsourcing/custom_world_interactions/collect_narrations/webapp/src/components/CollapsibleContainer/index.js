
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { useState, useEffect } from "react";

import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";

import "./styles.css";

const CollapsibleBox = ({ title, titleBg, containerBg, collapsedContent, children }) => {

  const [isCollapsed, setIsCollapsed] = useState(true);
  const openHandler = () => setIsCollapsed(false);
  const closeHandler = () => setIsCollapsed(true);

  const onIconClick = isCollapsed ? openHandler : closeHandler;
  const iconHelpText = isCollapsed ? "Expand" : "Collapse";
  const iconBody = isCollapsed ? <BiWindow color="white" /> : <FaWindowMinimize color="white" />;
  const expander = <div className="collapsible-header--icon" onClick={onIconClick}>
    <span className="collapsible-header--icon-text">{iconHelpText}</span>
    {iconBody}
  </div>

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
        {expander}
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
