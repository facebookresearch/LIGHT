/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppSelector } from "../../../../../app/hooks";
/* STYLES */
import "./styles.css";
/* ICONS */
import { GiSwapBag } from "react-icons/gi";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

const InventoryMessage = ({ text, onClickFunction }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ---- LOCAL STATE ---- */
  const [inventoryInfo, setInventoryInfo] = useState("");
  /* ---- LIFECYCLE ---- */
  useEffect(() => {
    let inventoryArr = text.split("\n");
    let inventory = inventoryArr[1];
    setInventoryInfo(inventory);
  }, [text]);
  return (
    <div className=" inventory-container">
      <div className="inventory-bag__container">
        <GiSwapBag className="inventory-bag" color="#bf8315" size="19em" />
        <div
          className={`inventory-content ${inHelpMode ? "active" : ""}`}
          onClick={onClickFunction}
        >
          <p className="inventory-content__entry" style={{ marginTop: "1px" }}>
            <TutorialPopover
              tipNumber={11}
              open={inHelpMode && selectedTip === 11}
              position="left"
            >
              {inventoryInfo}
            </TutorialPopover>
          </p>
        </div>
      </div>
    </div>
  );
};
export default InventoryMessage;
