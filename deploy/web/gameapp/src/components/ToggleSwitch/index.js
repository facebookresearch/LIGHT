/* REACT */
import React from "react";

import { Tooltip } from "react-tippy";
/* STYLES */
import "./styles.css";

const ToggleSwitch = ({ isOn, setOn, setOff, toolTipText, switchLabel }) => {
  const toggle = () => {
    if (isOn) {
      setOff();
    } else {
      setOn();
    }
  };
  return (
    <div className="toggle-container ">
      <span className="toggle-label">{switchLabel}</span>
      <Tooltip title={toolTipText}>
        <label className="toggle-switch">
          <input type="checkbox" checked={isOn} onChange={toggle} />
          <span className="switch" />
        </label>
      </Tooltip>
    </div>
  );
};

export default ToggleSwitch;
