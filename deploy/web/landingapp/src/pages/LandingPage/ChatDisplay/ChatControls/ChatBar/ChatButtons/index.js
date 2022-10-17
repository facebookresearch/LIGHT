/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* CUSTOM COMPONENTS */

import { getActionThemeColor } from "../../../../../../app/theme";

import { BiChevronRight } from "react-icons/bi";
import { FaSort } from "react-icons/fa";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatButtons = ({ action, toggleAction }) => {
  return (
    <div className="_chat-button_ h-full">
      <button
        onClick={(e) => {
          e.preventDefault();
          toggleAction();
        }}
        type="button"
        className={`h-full text-md font-medium rounded shadow-sm text-white pl-2 pr-4 ${getActionThemeColor(
          "bg",
          action
        )} hover:bg-white`}
      >
        <span className="flex flex-row items-center text-accent-content capitalize">
          {<FaSort />}
          <div className="capitalize pl-1">{`${action}`}</div>
        </span>
      </button>
    </div>
  );
};

export default ChatButtons;
