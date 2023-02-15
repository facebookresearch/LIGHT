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
import { BiRightArrow } from "react-icons/bi";

// MobileDrawer - Hides and renders children with side orientation
const MobileDrawer = ({
  isDrawerOpen,
  openDrawerFunction,
  closeDrawerFunction,
  children,
}) => {
  /*--------------- LOCAL STATE ----------------*/
  /*--------------- LIFECYLCLE ----------------*/

  /*--------------- HANDLERS ----------------*/
  return (
    <>
      <div
        style={{
          backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
        }}
        className={`_mobiledrawer-container_ fixed w-full top-0 left-0 overflow-scroll z-10 bg-gray-900 bg-opacity-25 inset-0
            ${
              isDrawerOpen ? "translate-x-0" : "-translate-x-full"
            } ease-in-out duration-300`}
      >
        <div className="_mobiledrawer-body_ flex flex-row w-screen h-screen">
          <div className="_mobiledrawer_content_ flex">{children}</div>
          <div className="_mobiledrawer-closebutton_ h-full flex justify-center items-center">
            <BiLeftArrow
              color="yellow"
              size={30}
              onClick={closeDrawerFunction}
            />
          </div>
        </div>
      </div>
      <div className="_arrow-container_ w-30 h-full flex items-center justify-center">
        <BiRightArrow onClick={openDrawerFunction} color="yellow" size={30} />
      </div>
    </>
  );
};

export default MobileDrawer;
