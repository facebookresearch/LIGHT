/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import PreviewContent from "./PreviewContent"

//PreviewView - Renders orientation info and preview of task
const PreviewView = () => {
  return (
    <div className="previewview-container">
      <div className="previewinfo-container">
        <div className="previewinfo-header">
            <h1 className="previewinfo-header__text">
              Fantasy Text Adventure Gameplay Task
            </h1>
        </div>
        <PreviewContent />
      </div>
    </div>
  );
};

export default PreviewView;
