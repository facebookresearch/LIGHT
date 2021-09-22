/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* ICONS */
import { GiSwapBag } from "react-icons/gi";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

const InventoryMessage = ({ text }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    dispatch(updateSelectedTip(tipNumber));
  };
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
        <div className="inventory-content">
          <p className="inventory-content__entry" style={{ marginTop: "1px" }}>
            <TutorialPopover
              tipNumber={0}
              open={inHelpMode && selectedTip === 0}
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
