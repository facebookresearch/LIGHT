
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import "./styles.css";
//CUSTOM COMPONENTS
import TaskDescription from "../../components/TaskDescription";

const Preview = ()=> {
  return (
    <div className="app-container" >
        <div className="header">
          <h1 className="header__text">Object Interaction Narrations</h1>
        </div>
      <TaskDescription/>
    </div>
  );
}

export default Preview ;
