/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";

/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

const SettingMessage = ({ text, onClickFunction }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  return (
    <div className="border-b border-b-[#ffffff33] border-dotted pb-4 mb-4">
      <div
        className={`${inHelpMode ? "active" : ""} prose font-mono text-white `}
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
