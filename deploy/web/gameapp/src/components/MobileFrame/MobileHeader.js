/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import { updateShowDrawer } from "../../features/view/view-slice";
import { updateSelectedTip } from "../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
//IMAGES
import Scribe from "../../assets/images/scribe.png";
//CUSTOM COMPONENTS
import ToggleSwitch from "../ToggleSwitch";
import IconButton from "../IconButtons/InfoButton";

// MobileHeader -
const MobileHeader = ({}) => {
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* REDUX STATE */
  //IsMobile
  const isMobile = useAppSelector((state) => state.view.isMobile);
  //DRAWER
  const showDrawer = useAppSelector((state) => state.view.showDrawer);
  /* REDUX ACTIONS */
  const openDrawer = () => {
    if (isMobile) {
      dispatch(updateSelectedTip(0));
    }
    dispatch(updateShowDrawer(true));
  };
  const closeDrawer = () => {
    if (isMobile) {
      dispatch(updateSelectedTip(0));
    }
    dispatch(updateShowDrawer(false));
  };

  return (
    <div className="mobileheader-container">
      <div className="mobileheader-logo">
        <img className="mobileheader-logo__img" src={Scribe} />
        <span className="mobileheader-logo__text"> LIGHT</span>
      </div>
      <div className="mobileheader-tools">
        <ToggleSwitch
          switchLabel="CHARACTER INFO"
          toolTipText={
            showDrawer
              ? "Click to return to the game"
              : "Click to open your character info."
          }
          isOn={showDrawer}
          setOn={openDrawer}
          setOff={closeDrawer}
        />
        <IconButton />
      </div>
    </div>
  );
};

export default MobileHeader;
