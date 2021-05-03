import React from "react";

import "../styles.css";
//IMAGE
import InteractingTell from "../../../assets/images/screenshots/Tutorial/Interacting/InteractingTell.png";
import InteractingWhisper from "../../../assets/images/screenshots/Tutorial/Interacting/InteractingWhisper.png";
import InteractingShout from "../../../assets/images/screenshots/Tutorial/Interacting/InteractingShout.png";
import InteractingRespond from "../../../assets/images/screenshots/Tutorial/Interacting/InteractingRespond.png";
import Emote1 from "../../../assets/images/screenshots/Tutorial/Interacting/Emote1.png";
import Emote2 from "../../../assets/images/screenshots/Tutorial/Interacting/Emote2.png";

const InteractingWithTheWorld = (props) => {
  return (
    <div className="interactingWiththeworld-container">
      <h1>Interacting with the World</h1>
      <h4>Talking</h4>
      <p>
        As you have already seen, talking is one of the most important parts of
        playing your role in the world of LIGHT. You can say, whisper, shout or
        tell something to other individuals — all using free-form text, e.g.tell
        the smithy “I’d love to own such a fine tool! It looks like wonderful
        craftsmanship, well done!” . Here are the example commands:
      </p>
      <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
        <img className="tutorialpage-image__half" src={InteractingTell} />
        <img className="tutorialpage-image__half" src={InteractingWhisper} />
        <img className="tutorialpage-image__quarter" src={InteractingShout} />
        <img className="tutorialpage-image__quarter" src={InteractingRespond} />
      </div>
      <p>
        Using a whisper command, only the other speaker can hear it. A *tell*
        command is directed to a speaker, but others in the room can hear it.
        The *shout* command may be heard by people also in nearby rooms. Just
        putting quotes around what you want to say (“Mmmm I wonder what is
        cooking”) can be heard by everyone in the room and is not necessarily
        directed at anyone in particular.
      </p>
      <h4>Showing Emotions</h4>
      <p>
        You can also express your emotions in the game with _emote actions_,
        e.g. smile, grin, scream or dance. The full list is: laugh, cry,
        smile,ponder,blush,shrug,sigh, wink, yawn, wave, stare, scream, pout,
        nudge, nod, growl, groan, grin, gasp, frown, dance, applaud.
      </p>
      <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
        <img className="tutorialpage-image__quarter" src={Emote1} />
        <img className="tutorialpage-image__quarter" src={Emote2} />
      </div>
    </div>
  );
};

export default InteractingWithTheWorld;
