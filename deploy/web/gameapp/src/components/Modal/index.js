import React, { useState, useEffect } from "react";

import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";

import "./styles.css";

const CollapsibleBox = ({ showModal, setModal, children }) => {
  const openHandler = () => setModal(true);
  const closeHandler = () => setModal(false);

  return (
    <div className="modal-overlay">
      <div className="modal-window">{children}</div>
    </div>
  );
};

export default CollapsibleBox;
