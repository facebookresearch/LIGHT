/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
//STYLE
import "../styles.css";
//IMAGES
import ExperienceImg1 from "../../../assets/images/screenshots/Tutorial/ExpSystem/ExpSystem1.png";
import ExperienceImg2 from "../../../assets/images/screenshots/Tutorial/ExpSystem/ExpSystem2.png";
import AwardExperience1 from "../../../assets/images/screenshots/Tutorial/AwardExp/AwardExp1.png";
import AwardExperience2 from "../../../assets/images/screenshots/Tutorial/AwardExp/AwardExp2.png";
import ReportPlayer1 from "../../../assets/images/screenshots/Tutorial/ReportPlayer/ReportPlayer1.png";

const ExperiencePointsSystem = (props) => {
  return (
    <div className="experiencepointssystem-container">
      <h1 className="tutorial-header">Experience Points System</h1>
      <h4 className="tutorial-subheader">Receiving Experience Points</h4>
      <p className="tutorial-text">
        Playing your role well will earn you experience points (EXP). For
        example playing the role of the jailer here with the following message
        to a goblin earns 4 EXP, as can be seen from the yellow star next to the
        message.
      </p>
      <img className="tutorialpage-image__row" src={ExperienceImg1} />
      <p className="tutorial-text">
        You can see your overall experience points and level in the top left
        panel. Earn enough experience to rise to the next level!
      </p>
      <img className="tutorialpage-image__quarter" src={ExperienceImg2} />
      <p className="tutorial-text">
        This panel also tells you your character’s persona, and their mission.
        Roleplaying your character well means playing this described role!
      </p>
      <h4 className="tutorial-subheader">Awarding Experience Points</h4>
      <p className="tutorial-text">
        If you believe another character is playing their role well, you can
        award them experience points! You can see your gift experience points in
        the star at the top left panel (shown here with 9 gift experience points
        with the mouse pointer resting over it):
      </p>
      <img className="tutorialpage-image__half" src={AwardExperience1} />
      <p className="tutorial-text">
        To gift experience points, simply click on the message from your partner
        that you deemed worthy of praise:
      </p>
      <img className="tutorialpage-image__row" src={AwardExperience2} />
      <h4 className="tutorial-subheader">Reporting Players</h4>
      <p className="tutorial-text">
        If you see bad behavior by any player, you can report it. This could
        include clearly not playing their role, or offensive messages. To report
        it simply click on the flag icon next to their message:
      </p>
      <img className="tutorialpage-image__half" src={ReportPlayer1} />
    </div>
  );
};

export default ExperiencePointsSystem;
