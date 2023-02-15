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

//IconCollapsibleBox - Renders collapsible container with selectible icon in header.
//* This component has been disconnected in the landing app and the emoji feature
//* is scheduled to be removed soon  11/1/2022
const IconCollapsibleBox = ({
  selectedEmoji,
  title,
  containerBg,
  children,
}) => {
  /* LOCAL STATE */
  const [isCollapsed, setIsCollapsed] = useState(false);
  /*  HANDLERS */
  //openHandler - Shows contents of container
  const openHandler = () => setIsCollapsed(false);
  //closeHandler - Hides contents of container
  const closeHandler = () => setIsCollapsed(true);

  return (
    <div className={`collapsible-container__icon`}>
      <div className={`collapsible-box__icon`}></div>
      <div className={`content-container `}>
        <div
          className={`collapsible-header`}
          style={{
            borderRadius: isCollapsed ? "15px" : null,
          }}
        >
          <div />
          <h5 className="collapsible-header--text">{title}</h5>
          <div className="collapsible-header--icon">
            {isCollapsed ? (
              <BsPlusLg color="white" onClick={openHandler} />
            ) : (
              <FaWindowMinimize color="white" onClick={closeHandler} />
            )}
          </div>
        </div>
        <div />
        {isCollapsed ? null : (
          <div
            className={`collapsible-body`}
            style={{ backgroundColor: containerBg, animation: null }}
          >
            {children}
          </div>
        )}
      </div>
    </div>
  );
};

export default IconCollapsibleBox;
