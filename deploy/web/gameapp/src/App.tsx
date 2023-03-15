/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REDUX */
import { useAppSelector } from "./app/hooks";
//ROUTES
import Routes from "./GameRouter";
/* IMAGES */
//APP BACKGROUND IMAGE
import StarryNight from "./assets/images/light_starry_bg.jpg";
//STYLES
import "./styles.css";

function App() {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);

  return (
    <div
      id={`${inHelpMode ? "helpmode" : ""}`}
      data-theme="light"
      style={{
        backgroundImage: `linear-gradient(to bottom, #0f0c2999, #302b63aa, #24243ecc), url(${StarryNight})`,
      }}
      className="__landing-page__ flex h-screen w-screen bg-cover bg-top bg-no-repeat overflow-x-scroll min-w-[75%]"
    >
      <Routes />
    </div>
  );
}

export default App;
