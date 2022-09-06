
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

//PlayerMessage - Renders message sent by player to chat with custom styling and displays any xp awarded to message
const PlayerMessage = ({
  text,
  speaker,
  }) => {
  let classNames = "message type-dialogue ";
  classNames += "me";

  return (
    <div
      className={`${classNames}`}
    >
        <div className="agent">
          <span id="message-nameplate">
            {speaker.toUpperCase()}
          </span>
        </div>
        {text}
    </div>
  );
};
export default PlayerMessage;
