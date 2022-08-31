
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* STYLES */
import "./styles.css";

const AgentMessage = ({
  text,
  speaker
}) => {
  let classNames = "message type-dialogue ";
  // if (["tell", "say", "whisper"].includes(caller)) {
  //   text = "&ldquo;" + text + "&rdquo;";
  //   classNames = "message type-dialogue ";
  // }
  classNames += "other";

  return (
    <div
      className={`${classNames}`}

    >
        <div className="agent">
          <span id="message-nameplate">
            {speaker.toUpperCase()}
          </span>
          {
            <div className="message-icon__container">

                <div style={{ position: "relative", marginRight: "150%" }}>
                  {
                    <i
                      id="message-star-O"
                      className="fa fa-star-o "
                    />
                  }
                </div>
            </div>
          }
        </div>
        {text}
    </div>
  );
};
export default AgentMessage;
