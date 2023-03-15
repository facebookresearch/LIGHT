/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";

// DisconnectMessage - Renders Disconnect messagee and reload link upon player being idle for too long
const DisconnectMessage = () => {
  return (
    <div className="_disconnect-container_ flex w-full flex-col justify-center items-center">
      <h2 className=" _disconnect-text_ text-xl text-blue-100">
        You have been disconnected due to inactivity.
      </h2>
      <h2
        onClick={() => window.location.reload()}
        style={{ textDecoration: "underline" }}
        className="_disconnect-text__reload_ text-xl text-white underline"
      >
        Click Here to re-enter world.
      </h2>
    </div>
  );
};

export default DisconnectMessage;
