import React from "react";
import "./styles.css";

const ToggleSwitch = ({ isOn, setOn, setOff }) => {
  const toggle = () => {
    if (isOn) {
      setOff();
    } else {
      setOn();
    }
  };
  return (
    <label className="toggle-switch">
      <input type="checkbox" checked={isOn} onChange={toggle} />
      <span className="switch" />
    </label>
  );
};

export default ToggleSwitch;
