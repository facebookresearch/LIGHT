/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React from "react";
/* IMAGES */
import Scribe from "./assets/images/scribe.png";

// Logo - Renders Light Logo
const Logo = ()=> {
  return (
    <div className="_logo-container_ w-full flex flex-col items-center mb-4">
      <img className="_logo-image_ w-1/3" alt="logo" src={Scribe} />
      <div className="_logo-text_ flex flex-col justify-center items-center">
        <h1 className="_logo-header_ text-4xl">LIGHT</h1>
        <span className="_logo-subheader_ text-center">Learning in Interactive Games with Humans and Text</span>
      </div>
    </div>
  );
}

export default Logo;