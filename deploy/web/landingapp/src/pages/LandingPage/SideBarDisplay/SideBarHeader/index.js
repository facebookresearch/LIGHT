/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
//CUSTOM COMPONENTS
import ProgressBar from "../../../../components/Progressbar";
/* IMAGES */
import Scribe from "../../../../assets/images/scribe.png";

//SidebarHeader - Renders user info and progress at the top of the side bar.  (hard coded in Landing App)
const SidebarHeader = () => {
  return (
    <>
      <div className="__sidebar_header_container__ flex flex-row justify-start items-center w-full">
        <div className="__sidebar_header_info_container__ flex flex-row justify-start items-center w-3/4 pt-2 pl-2">
          <img
            className="__scribe-avatar__  inline-block h-14 w-14 rounded-full mr-2"
            src={Scribe}
          />
          <div className="__sidebar_header_info_progressbar_container__ w-full">
            <p style={{ color: "white" }}> {`You are level 1`} </p>
            <ProgressBar />
          </div>
        </div>
      </div>
    </>
  );
};

export default SidebarHeader;
