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
        {buttons.map((button, index) => (
          <GlowingButton
            id={index}
            label={button.label}
            buttonFunction={button.clickFunction}
          />
        ))}
      </div>
    </div>
  );
};

export default MobileHeader;
