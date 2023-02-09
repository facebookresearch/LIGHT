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
const GiftStar = ({giftXp, isLiked, isStarred, onClick }) => {
  return (
    <div className="_star-container_">
        {
        isStarred ? (
                <BsFillStarFill id="gift-star" className={`text-yellow-400`} />
              ) : isLiked ? (
                <Tooltip
                  title={giftXp>0 ? "Click to award player a Gift XP Star":"Role play to earn Gift XP"}
                  position="top"
                >
                  <BsStar className='text-yellow-400' onClick={onClick} />
                </Tooltip>
              ) : null} 
    </div>
  );
};

export default GiftStar;