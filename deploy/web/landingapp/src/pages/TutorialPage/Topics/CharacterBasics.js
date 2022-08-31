/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import "../styles.css";

//IMAGES
import CharacterBasicsQuest from "../../../assets/images/screenshots/Tutorial/CharacterBasics/CharacterBasicsQuest.png";
import CharacterBasicsInventory from "../../../assets/images/screenshots/Tutorial/CharacterBasics/CharacterBasicsInventory.png";
import CharacterBasicsStats from "../../../assets/images/screenshots/Tutorial/CharacterBasics/CharacterBasicsStats.png";

const CharacterBasics = (props) => {
  return (
    <div className="characterbasics-container">
      <h1 className="tutorial-header">Character Basics</h1>
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Quest: </span>If you want to be
        reminded what character you are playing and your goals type “quest”:
      </p>
      <img className="tutorialpage-image__75" src={CharacterBasicsQuest} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Inventory: </span>To see what you
        are carrying you can type “inventory” or “inv” or even “i” for short:
      </p>
      <img className="tutorialpage-image__75" src={CharacterBasicsInventory} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Stats: </span>To see your stats,
        type “stats:
      </p>
      <img className="tutorialpage-image__quarter" src={CharacterBasicsStats} />
      <p className="tutorial-text">
        Help! You can also type “help” at any time to see a short list of
        instructions.
      </p>
    </div>
  );
};

export default CharacterBasics;
