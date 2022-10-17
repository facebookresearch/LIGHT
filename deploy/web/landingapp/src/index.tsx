/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
import ReactDOM from "react-dom";
/* STYLES */
import "./index.css";
/* CUSTOM COMPONENTS */
import AppRouter from "./AppRouter";

const rootElement = document.getElementById("root");

ReactDOM.render(<AppRouter />, rootElement);
