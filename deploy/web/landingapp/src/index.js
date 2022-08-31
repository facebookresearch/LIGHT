/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import ReactDOM from "react-dom";
import "./styles.css";

import AppRouter from "./AppRouter";

const rootElement = document.getElementById("root");

ReactDOM.render(<AppRouter />, rootElement);
