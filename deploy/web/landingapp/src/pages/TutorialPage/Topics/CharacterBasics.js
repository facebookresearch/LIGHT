import React from "react";

import "../styles.css";

const CharacterBasics = (props) => {
  return (
    <div className="characterbasics-container">
      <h1>Character Basics</h1>
      <p>
        Quest: If you want to be reminded what character you are playing and
        your goals type “quest”:
      </p>
      <p>
        Inventory: To see what you are carrying you can type “inventory” or
        “inv” or even “i” for short:
      </p>
      <p>Stats: To see your stats, type “stats:</p>
      <p>
        Help! You can also type “help” at any time to see a short list of
        instructions.
      </p>
    </div>
  );
};

export default CharacterBasics;
