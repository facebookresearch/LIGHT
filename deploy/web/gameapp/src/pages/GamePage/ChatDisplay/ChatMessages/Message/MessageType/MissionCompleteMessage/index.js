/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* ICONS */
import { FaStar } from "react-icons/fa";

const MissionCompleteMessage = ({ xp, name }) => {
  return (
    <div className=" w-full flex justify-center items-center mb-4">
      <div
        className={`_missionsuccess-container_
        border-double border-8 rounded border-yellow-300 flex flex-col justify-center items-center p-4
        font-mono text-yellow-300 text-center
      `}
      >
        <p className="_missionsuccess-header_ font-bold text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl  2xl:text-5xl">
          MISSION SUCCESS!
        </p>
        <FaStar className="_missionsuccess-star_" color="yellow" size="10em" />
        <h1 className="_missionsuccess-star__exp_ text-lg sm:text-xl md:text-2xl lg:text-3xl xl:text-4xl  2xl:text-5xl">
          {xp}XP
        </h1>
        <div className="_missionsuccess-banner_">
          <p
            className="_missionsuccess-banner__text_ text-sm sm:text-sm md:text-base lg:text-lg xl:text-xl  2xl:text-2xl"
            style={{ marginTop: "1px" }}
          >
            {name}
          </p>
        </div>
      </div>
    </div>
  );
};
export default MissionCompleteMessage;
