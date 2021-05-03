import React from "react";
//STYLE
import "../styles.css";
//IMAGES
import ExperienceImg1 from "../../../assets/images/screenshots/Tutorial/ExpSystem/ExpSystem1.png";
import ExperienceImg2 from "../../../assets/images/screenshots/Tutorial/ExpSystem/ExpSystem2.png";

const ExperiencePointsSystem = (props) => {
  return (
    <div className="experiencepointssystem-container">
      <h1>Exprience Points System</h1>
      <h4>Receiving Experience Points</h4>
      <p>
        Playing your role well will earn you experience points (EXP). For
        example playing the role of the jailer here with the following message
        to a goblin earns 4 EXP, as can be seen from the yellow star next to the
        message.
      </p>
      <img src={ExperienceImg1} />
      <p>
        You can see your overall experience points and level in the top left
        panel. Earn enough experience to rise to the next level!
      </p>
      <img src={ExperienceImg2} />
      <p>
        This panel also tells you your character’s persona, and their mission.
        Roleplaying your character well means playing this described role!
      </p>
    </div>
  );
};

export default ExperiencePointsSystem;
