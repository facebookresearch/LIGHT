import React from "react";
import "./styles.css";
//CUSTOM COMPONENTS
import MobileHeader from "./MobileHeader";

const MobileFrame = ({
  showDrawer,
  openDrawer,
  closeDrawer,
  buttons,
  children,
}) => {
  return (
    <div className="mobile-container">
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
