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
    <div className="_star-container_ flex justify-center items-center w-10 h-10 bg-orange-500">
        <div className="relative flex justify-center items-center bg-blue-600">
            <span className="absolute  bg-red-500">
                <BsFillStarFill  className=" message-star text-4xl left-0 right-0 m-auto" color="yellow" />
            </span>
            <div className="absolute flex left-0 right-0 m-auto justify-center items-center bg-green-500" >
                <span  className="message-star__number text-black">{xp}</span>
            </div>
        </div>
    </div>
  );
};

export default AwardStar;
