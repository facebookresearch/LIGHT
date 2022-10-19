/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";

const TerminalEntry = ({ text, highlighted }) => {
  return (
    <p className={`${highlighted ? "text-green-200" : "text-white"}`}>{text}</p>
  );
};

export default TerminalEntry;
