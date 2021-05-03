import React from "react";

import "../styles.css";

//IMAGES
import CharacterBasicsQuest from "../../../assets/images/screenshots/Tutorial/CharacterBasics/CharacterBasicsQuest.png";
import CharacterBasicsInventory from "../../../assets/images/screenshots/Tutorial/CharacterBasics/CharacterBasicsInventory.png";
import CharacterBasicsStats from "../../../assets/images/screenshots/Tutorial/CharacterBasics/CharacterBasicsStats.png";

const CharacterBasics = (props) => {
  return (
    <div className="characterbasics-container">
      <h1>Character Basics</h1>
      <p>
        Quest: If you want to be reminded what character you are playing and
        your goals type “quest”:
      </p>
      <img className="tutorialpage-image__75" src={CharacterBasicsQuest} />
      <p>
        Inventory: To see what you are carrying you can type “inventory” or
        “inv” or even “i” for short:
      </p>
      <img className="tutorialpage-image__75" src={CharacterBasicsInventory} />
      <p>Stats: To see your stats, type “stats:</p>
      <img className="tutorialpage-image__quarter" src={CharacterBasicsStats} />
      <p>
        Help! You can also type “help” at any time to see a short list of
        instructions.
      </p>
    </div>
  );
};

export default CharacterBasics;
