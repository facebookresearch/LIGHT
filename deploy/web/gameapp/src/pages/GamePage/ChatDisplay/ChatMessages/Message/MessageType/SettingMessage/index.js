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
    <TutorialPopover
      tipNumber={15}
      open={inHelpMode && selectedTip === 15}
      position="bottom"
    >
      <div className="_message-row_ w-full flex justify-center item-center mb-4">
          <div
            className={`${
              inHelpMode ? "active" : ""
            } _setting-container_ w-5/6 md:w-2/3 flex border-solid border-4 rounded border-white justify-center items-center p-4`}
          >
            <div
              className={`_setting-body_ prose text-white text-md`}
              onClick={onClickFunction}
            >
              {text.split("\n").map((para, idx) => (
                <p key={idx}>{para}</p>
              ))}
            </div>
          </div>
      </div>
    </TutorialPopover>
  );
};
export default SettingMessage;
