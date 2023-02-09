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
    <TutorialPopover
    tipNumber={11}
    open={inHelpMode && selectedTip === 11}
    position="bottom"
  >
    <div className="_message-row_ w-full flex justify-center items-center mb-4">
        <div
          className={`_inventory-container_ ${inHelpMode ? "active" : ""}
          w-5/6 md:w-2/3 flex border-solid border-4 rounded border-white justify-center items-center p-4 `}
          onClick={onClickFunction}
        >
          <div className="_inventory-content_ w-full flex flex-col justify-center items-center text-white">
            <div className="_inventory-content-header_ w-full flex flex-row justify-center items-center ">
              <p className="_help-content-header-text_ font-bold">INVENTORY</p>
              <GiSwapBag className="_help-content-header-icon_ text-white  ml-2"/>
            </div>
            <p className="_inventory-content-entry_ text-center text-md mt-1">{inventoryInfo}</p>
          </div>
        </div>
    </div>
    </TutorialPopover>
  );
};
export default InventoryMessage;
