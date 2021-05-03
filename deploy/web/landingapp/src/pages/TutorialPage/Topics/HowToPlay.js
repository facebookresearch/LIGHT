import React from "react";

import "../styles.css";

const HowToPlay = (props) => {
  return (
    <div className="howtoplay-container">
      <h1 className="tutorial-header">How to Play LIGHT</h1>
      <p className="tutorial-text">
        You will be teleported into our mystical realm and fill the shoes of a
        character who lives there — playing that role you must act and talk with
        other LIGHT denizens. As you interact, your messages will be evaluated
        by the Dungeon Master AI. Portray your character well and you will
        increase your{" "}
        <span style={{ fontWeight: "bolder" }}>experience points</span>. Other
        characters will also be playing their roles as well — some of them will
        be other human souls, others will be AIs. When everyone is playing their
        role to the best of their ability in the realm the experience will be
        maximized. You can <span style={{ fontWeight: "bolder" }}>reward </span>
        other players when you are impressed by their skills. You can also
        <span style={{ fontWeight: "bolder" }}> report</span> or demote unwanted
        behaviors: e.g., mentions of the real world or bad behavior. Stay good,
        my denizens!
      </p>
    </div>
  );
};

export default HowToPlay;
