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

// SideDrawer - Hides and renders children with side orientation
const SideDrawer = ({
  isDrawerOpen,
  openDrawerFunction,
  closeDrawerFunction,
  children,
}) => {
  /*--------------- LIFECYLCLE ----------------*/

  /*--------------- HANDLERS ----------------*/
  return (
    <>
      {isDrawerOpen ? (
        <div
          style={{
            backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
          }}
          className={
            "__mobiledrawer-container__ fixed overflow-scroll z-10 bg-gray-900 bg-opacity-25 inset-0 transform ease-in-out " +
            (isDrawerOpen
              ? " transition-opacity opacity-100 duration-500 translate-x-0  "
              : " transition-all delay-500 opacity-0 translate-x-full  ")
          }
        >
          <div className="__mobiledrawer-body__ flex flex-row w-screen h-screen">
            <div className="__mobiledrawer_content__ flex">{children}</div>
            <div className="__mobiledrawer-closebutton__ h-full flex justify-center items-center">
              <BiLeftArrow
                color="yellow"
                size={30}
                onClick={closeDrawerFunction}
              />
            </div>
          </div>
        </div>
      ) : (
        <div className=" w-30 h-full flex items-center justify-center">
          <BiRightArrow onClick={openDrawerFunction} color="yellow" size={30} />
        </div>
      )}
    </>
  );
};

export default SideDrawer;
