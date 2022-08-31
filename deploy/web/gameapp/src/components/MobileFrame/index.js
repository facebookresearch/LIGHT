/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import MobileHeader from "./MobileHeader";

const MobileFrame = ({
  showDrawer,
  openDrawer,
  closeDrawer,
  buttons,
  children,
}) => {
  return (
    <div id="mobile-container">
      <MobileHeader
        buttons={buttons}
        showDrawer={showDrawer}
        openDrawer={openDrawer}
        closeDrawer={closeDrawer}
      />
      <div className="mobile-content">{children}</div>
    </div>
  );
};

export default MobileFrame;
