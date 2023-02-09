/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppSelector } from "../../../../../../../app/hooks";
/* STYLES */
import "./styles.css";
/* ICONS */
import { GiSwapBag } from "react-icons/gi";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../../components/TutorialPopover";

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
    <div className=" w-full flex justify-center items-center mb-4">
      <TutorialPopover
        tipNumber={11}
        open={inHelpMode && selectedTip === 11}
        position="bottom"
      >
        <div
          className={`_inventory-container_ ${inHelpMode ? "active" : ""}
        border-solid border-4 rounded border-green-300 flex justify-center items-center p-4 `}
          onClick={onClickFunction}
        >
          <div className="_inventory-content_ text-green-300 text-center text-md">
            <p className="_inventory-content-entry_ mt-1">{inventoryInfo}</p>
          </div>
        </div>
      </TutorialPopover>
    </div>
  );
};
export default InventoryMessage;
