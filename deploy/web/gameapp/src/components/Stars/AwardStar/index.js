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
import { BsFillStarFill } from "react-icons/bs";

//AwardStar - Renders star with amount of experience earned in the center
const AwardStar = ({ xp }) => {
  return (
    <div className="_awardstar-container_ flex justify-center items-center w-10 h-10 mr-4">
        <div className="_awardstar_ relative flex justify-center items-center">
            <span className="_star-container_ absolute ">
                <BsFillStarFill  className=" _star_ text-4xl left-0 right-0 m-auto" color="yellow" />
            </span>
            <div className="_award-number-container_ absolute flex left-0 right-0 m-auto justify-center items-center bg-green-500" >
                <span  className="_award-number_ pt-1 text-black text-xs font-bold opacity-60">{xp}</span>
            </div>
        </div>
    </div>
  );
};

export default AwardStar;
