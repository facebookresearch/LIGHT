/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
/* STYLES */
import "./styles.css";

// Modal - generates modal frame with overlay
const SideDrawer = () => {
  return (
    <div className="sidedrawer w-1/4">
      <div className=""></div>
      <div className=""></div>
      <div className="">
        <div className="tabs tabs-boxed">
          <a className="tab">Tab 1</a>
          <a className="tab tab-active">Tab 2</a>
          <a className="tab">Tab 3</a>
        </div>
      </div>
    </div>
  );
};

export default SideDrawer;
