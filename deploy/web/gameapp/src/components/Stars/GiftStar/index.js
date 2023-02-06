/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* ICONS */
import { BsFillStarFill } from "react-icons/bs";
import { BsStar } from "react-icons/bs";

//GiftStar - 
const GiftStar = ({isLiked, isStarred, onClick }) => {
  return (
    <div className="_star-container_">
        {
        true ? (
                <BsFillStarFill className={`text-yellow-300`} />
              ) : isLiked > 0 ? (
                <Tooltip
                  title="Click to ward player a Gift XP Star"
                  position="top"
                >
                  <BsStar className='text-black' onClick={onClick} />
                </Tooltip>
              ) : null} 
    </div>
  );
};

export default GiftStar;