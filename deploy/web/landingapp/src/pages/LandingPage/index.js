/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { useState } from "react";
import { Link } from "react-router-dom";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";

import Scribe from "../../assets/images/scribe.png";
import StarryNight from "../../assets/images/light_starry_bg.jpg";
import "./styles.css";

const LandingPage = (props) => {
  let [page, setPage] = useState(0);

  const pageChangeHandler = (arrow) => {
    if (page > 0 && arrow === "-") {
      let previousPage = (page -= 1);
      setPage(previousPage);
    } else if (page < 2 && arrow === "+") {
      let nextPage = (page += 1);
      setPage(nextPage);
    }
  };
  return (
    <div
      style={{
        backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
      }}
      className="__landing-page__ flex h-screen w-screen bg-cover bg-top bg-no-repeat"
    >
      <h1 className="header-text">Welcome to the world of LIGHT</h1>
    </div>
  );
};

export default LandingPage;
