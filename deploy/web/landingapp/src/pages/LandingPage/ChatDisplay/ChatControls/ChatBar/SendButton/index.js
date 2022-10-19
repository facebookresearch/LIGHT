/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */

/* CUSTOM COMPONENTS */
import { getActionThemeColor } from "../../../../../../app/theme";

//ICONS
import { MdSend } from "react-icons/md";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const SendButton = ({ onSubmit, scrollToBottom, action }) => {
  /*---------------HANDLERS----------------*/
  const chatSubmissionHandler = (e) => {
    e.preventDefault();

    let textSubmission;
    if (!!chatText) {
      if (isSaying) {
        textSubmission = `"${chatText}"`;
      } else {
        textSubmission = chatText;
      }
      onSubmit(textSubmission);
      scrollToBottom();
    }
  };

  /*---------------HELPERS----------------*/

  return (
    <div
      className={`_send-button_ text-2xl ${getActionThemeColor(
        "text",
        action,
        false
      )} hover:text-white cursor-pointer px-2 py-2`}
    >
      <MdSend onClick={chatSubmissionHandler} />
    </div>
  );
};

export default SendButton;
