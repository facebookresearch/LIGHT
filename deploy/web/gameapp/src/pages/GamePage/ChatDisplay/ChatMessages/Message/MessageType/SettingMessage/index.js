/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../../../app/hooks";

/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../../components/TutorialPopover";

const SettingMessage = ({ text, onClickFunction }) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  return (
    <div className="w-full flex justify-center item-center mb-4">
      <div className=" border-dotted border-4 rounded border-white flex justify-center items-center p-4">
        <div
          className={`${
            inHelpMode ? "active" : ""
          } prose font-mono text-white text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl  2xl:text-2xl`}
          onClick={onClickFunction}
        >
          {text.split("\n").map((para, idx) => (
            <p key={idx}>{para}</p>
          ))}
        </div>
        <TutorialPopover
          tipNumber={15}
          open={inHelpMode && selectedTip === 15}
          position="bottom"
        />
      </div>
    </div>
  );
};
export default SettingMessage;
