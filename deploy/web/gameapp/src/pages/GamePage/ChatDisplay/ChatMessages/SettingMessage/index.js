/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

const SettingMessage = ({ text, onClickFunction }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  return (
    <div style={{ display: "flex", justifyContent: "center", width: "100%" }}>
      <div
        className={`setting-container ${inHelpMode ? "active" : ""}`}
        onClick={onClickFunction}
      >
        <TutorialPopover
          tipNumber={15}
          open={inHelpMode && selectedTip === 15}
          position="top"
        />
        {text.split("\n").map((para, idx) => (
          <p key={idx}>{para}</p>
        ))}
      </div>
    </div>
  );
};
export default SettingMessage;
