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

// MobileDrawer - Hides and renders children with side orientation
const MobileDrawer = ({ children, isDrawerOpen, setIsDrawerOpen }) => {
  /*--------------- LOCAL STATE ----------------*/
  /*--------------- LIFECYLCLE ----------------*/

  /*--------------- HANDLERS ----------------*/
  return (
    <div
      style={{
        backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
      }}
    >
      {children}
    </div>
  );
};

export default MobileDrawer;
