import React from "react";

const ToggleSwitch = ({ isOn, setOn, setOff }) => {
  const toggle = () => {
    if (isOn) {
      setOff();
    } else {
      setOn();
    }
  };
  return (
    <div className="toggle-switch">
      <input
        type="checkbox"
        className="toggle-switch-checkbox"
        name="toggleSwitch"
        id="toggleSwitch"
        checked={isOn}
        onChange={toggle}
      />
    </div>
  );
};

export default ToggleSwitch;
