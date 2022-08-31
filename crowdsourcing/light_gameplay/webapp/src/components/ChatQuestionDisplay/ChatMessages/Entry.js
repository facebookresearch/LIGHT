
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* MESSAGE COMPONENTS */
import PlayerMessage from "./PlayerMessage";
import AgentMessage from "./AgentMessage";

//Entry - Renders specific type of message component based on individual message object's attributes
const Entry = ({
  msg,
  speaker,
  isPlayer,
}) => {

  if (isPlayer) {
    return (
          <PlayerMessage
            text={msg}
            speaker={speaker}
          />
        )
  } else {
    return (
          <AgentMessage
            text={msg}
            speaker={speaker}
          />
        )
  }
};

export default Entry;
