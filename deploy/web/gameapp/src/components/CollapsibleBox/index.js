/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { updateSelectedTip } from "../../features/tutorials/tutorials-slice";
/* ICONS */
import { BsPlusLg } from "react-icons/bs";
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
  onClickFunction,
}) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  /* ----LOCAL STATE---- */
  const [isCollapsed, setIsCollapsed] = useState(false);
  const openHandler = () => setIsCollapsed(false);
  const closeHandler = () => setIsCollapsed(true);

  return (
    <div
      className={`collapsible-container ${inHelpMode ? "active" : ""} `}
      onClick={onClickFunction}
    >
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
            <BsPlusLg color="white" onClick={openHandler} />
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
