import React, { useState, useEffect } from "react";

import { GiSwapBag } from "react-icons/gi";
import { Tooltip } from "react-tippy";

const InventoryMessage = ({ text }) => {
  const [inventoryInfo, setInventoryInfo] = useState("");
  useEffect(() => {
    let inventoryArr = text.split("\n");
    let inventory = inventoryArr[1];
    setInventoryInfo(inventory);
  }, [text]);
  return (
    <div className=" inventory-container">
      <div className="inventory-bag__container">
        <GiSwapBag className="inventory-bag" color="#bf8315" size="19em" />
        <div className="inventory-content">
          <p className="inventory-content__entry" style={{ marginTop: "1px" }}>
            {inventoryInfo}
          </p>
        </div>
      </div>
    </div>
  );
};
export default InventoryMessage;
