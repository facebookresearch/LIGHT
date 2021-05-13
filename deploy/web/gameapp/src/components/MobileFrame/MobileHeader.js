import React from "react";
import "./styles.css";
//IMAGES
import Scribe from "../../assets/images/scribe.png";
//CUSTOM COMPONENTS
import GlowingButton from "../GlowingButton";
import ToggleSwitch from "../ToggleSwitch";

const MobileHeader = ({ buttons, showDrawer, openDrawer, closeDrawer }) => {
  return (
    <div className="mobileheader-container">
      <img className="mobileheader-img" src={Scribe} />
      <ToggleSwitch isOn={showDrawer} setOn={openDrawer} setOff={closeDrawer} />
      {buttons.map((button, index) => (
        <GlowingButton
          id={index}
          label={button.label}
          buttonFunction={button.clickFunction}
        />
      ))}
    </div>
  );
};

export default MobileHeader;
