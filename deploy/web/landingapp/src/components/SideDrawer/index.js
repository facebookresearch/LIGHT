/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* IMAGES */
//APP BACKGROUND IMAGE
import StarryNight from "../../assets/images/light_starry_bg.jpg";
/* ICONS */
import { BiLeftArrow } from "react-icons/bi";

// SideDrawer - Hides and renders children with side orientation
const SideDrawer = ({ children }) => {
  /*--------------- LOCAL STATE ----------------*/
  const [isDrawerOpen, setIsDrawerOpen] = useState(true);
  /*--------------- LIFECYLCLE ----------------*/

  /*--------------- HANDLERS ----------------*/
  return (
    <div
      style={{
        backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
      }}
      className={`top-0 right-0 w-[100vw] z-30 pb-20 text-white fixed h-full flex flex-row`}
    >
      {children}
      <div className="h-full flex justify-center">
        <BiLeftArrow color="yellow" size={30} />
      </div>
    </div>
  );
};

export default SideDrawer;
