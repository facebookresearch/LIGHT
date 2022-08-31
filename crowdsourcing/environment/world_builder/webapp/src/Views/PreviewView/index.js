/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
