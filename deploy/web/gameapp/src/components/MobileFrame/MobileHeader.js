import React from "react";
import "./styles.css";
//CUSTOM COMPONENTS
import GlowingButton from "../GlowingButton";
import ToggleSwitch from "../ToggleSwitch";

const MobileHeader = ({ buttons, showDrawer, openDrawer, closeDrawer }) => {
  return (
    <div className="mobile-container">
      <div className="mobile-header">
        <ToggleSwitch
          isOn={showDrawer}
          setOn={openDrawer}
          setOff={closeDrawer}
        />
        {}
      </div>
    </div>
  );
};

export default MobileHeader;
