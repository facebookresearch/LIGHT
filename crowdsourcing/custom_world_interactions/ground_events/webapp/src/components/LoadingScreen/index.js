
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//REACT
import React from "react";
//STYLING
import "./styles.css"

// loadingScreen - what will be rendered when mephisto isLoading prop is true
const LoadingScreen = ()=> {
  return (
    <section className="hero is-light">
      <div className="hero-body">
        <div className="container">
          <p className="subtitle is-5">Loading...</p>
        </div>
      </div>
    </section>
  );
}

export default LoadingScreen;
