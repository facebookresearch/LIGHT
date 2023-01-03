/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";

// SideDrawer - Hides and renders children with side orientation
const SideDrawer = ({ children }) => {
  /*--------------- LOCAL STATE ----------------*/
  const [isDrawerOpen, setIsDrawerOpen] = useState(true);
  /*--------------- LIFECYLCLE ----------------*/

  /*--------------- HANDLERS ----------------*/
  return (
    <div
      className={`top-0 right-0 w-[100vw] bg-blue-600 z-30 p-10 pl-20 text-white fixed h-full `}
    >
      {children}
    </div>
  );
};

export default SideDrawer;
