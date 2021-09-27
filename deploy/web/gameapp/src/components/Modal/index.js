/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

// Modal - generates modal frame with overlay
const Modal = ({ children }) => {
  return (
    <div className="modal-overlay">
      <div className="modal-window">{children}</div>
    </div>
  );
};

export default Modal;
