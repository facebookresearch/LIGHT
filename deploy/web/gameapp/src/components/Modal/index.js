/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
