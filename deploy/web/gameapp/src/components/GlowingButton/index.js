/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//GlowingButton - Renders button that glows with pulse animation on hover or activation.
const GlowingButton = ({ label, buttonFunction }) => {
  return (
    <div className="glowing-button" onClick={buttonFunction}>
      <span className="glowingbutton-text">{label}</span>
    </div>
  );
};

export default GlowingButton;
