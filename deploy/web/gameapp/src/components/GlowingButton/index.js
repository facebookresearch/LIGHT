import React from "react";
import "./styles.css";

const GlowingButton = ({ label, buttonFunction }) => {
  return (
    <div className="glowing-button" onClick={buttonFunction}>
      <span className="glowingbutton-text">{label}</span>
    </div>
  );
};

export default GlowingButton;
