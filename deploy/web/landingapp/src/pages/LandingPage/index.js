import React, { useState } from "react";
import { Link } from "react-router-dom";
import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";

import Scribe from "../../assets/images/scribe.png";
import "../../styles.css";

const LandingPage = (props) => {
  let [page, setPage] = useState(0);

  const pageChangeHandler = (arrow) => {
    console.log(page);
    if (page > 0 && arrow === "-") {
      let previousPage = (page -= 1);
      setPage(previousPage);
    } else if (page < 2 && arrow === "+") {
      let nextPage = (page += 1);
      setPage(nextPage);
    }
  };
  return (
    <div className="landingpage-container">
      <h1 className="header-text">Welcome to the world of LIGHT</h1>
      <div className="main-container">
        <div className="instructions-container">
          <div className="instructions-container__section">
            <div className="instruction-bubble">
              <div className="guide-container">
                <img className="guide-img" src={Scribe} />
                <div className="arrowbox">
                  {page !== 0 ? (
                    <div
                      onClick={() => pageChangeHandler("-")}
                      className="instruction-arrow__container"
                    >
                      <p className="instruction-arrow">{"<"}</p>
                    </div>
                  ) : (
                    <div style={{ width: "3em", margin: ".5em" }} />
                  )}
                  {page !== 2 ? (
                    <div
                      onClick={() => pageChangeHandler("+")}
                      className="instruction-arrow__container "
                    >
                      <p className="instruction-arrow">{">"}</p>
                    </div>
                  ) : (
                    <div style={{ width: "3em", margin: ".5em" }} />
                  )}
                </div>
              </div>
              <div className="instruction-text__container">
                {page == 0 ? (
                  <>
                    <p style={{ fontSize: "2.5em", textAlign: "center" }}>
                      The Dungeon Master is glad to see you.
                    </p>
                  </>
                ) : null}
                {page == 1 ? (
                  <>
                    <h2 style={{ color: "gold", textAlign: "center" }}>
                      Roleplay your Character
                    </h2>
                    <p>
                      You will be teleported into our mystical realm and fill
                      the shoes of a character who lives there — playing that
                      role you must act and talk with other LIGHT denizens. As
                      you interact, your messages will be evaluated by the
                      Dungeon Master AI. Portray your character well and you
                      will increase your <b>experience points</b>.
                    </p>
                    <p>
                      Other characters will also be playing their roles as well
                      — some of them will be other human souls, others will be
                      AIs. When everyone is playing their role to the best of
                      their ability in the realm the experience will be
                      maximized. You can <b>reward</b> other players when you
                      are impressed by their skills. You can also <b>report</b>{" "}
                      or demote unwanted behaviors: e.g., mentions of the real
                      world or bad behavior. Stay good, my denizens!
                    </p>
                  </>
                ) : null}
                {page == 2 ? (
                  <>
                    <h2 style={{ color: "gold", textAlign: "center" }}>
                      Interact with the World
                    </h2>
                    <p>
                      <b>Talking:</b> Talking is the most important part of
                      playing your role in the world. You can say, whisper,
                      shout or tell something to other individuals — all using
                      free-form text, e.g.
                      <i>
                        tell the smithy “I’d love to own such a fine tool! It
                        looks like wonderful craftsmanship, well done!”{" "}
                      </i>
                      .
                    </p>
                    <p>
                      <b>Emotes:</b> You can also express your emotions in the
                      game with
                       <u>emote actions</u>, e.g. <i>smile, grin, scream</i> or{" "}
                      <i>dance</i>.
                    </p>
                    <p>
                      <b>Actions:</b> You can move into new locations (e.g.,{" "}
                      <i>go west</i>), pick up objects (e.g., <i>get tool</i>),
                      give objects (e.g.,
                       <i>give tool to smithy</i>), wear clothing, wield weapons,
                      eat, drink, try to steal objects, and more. Type <i>help</i>
                      in game for the full list of actions.
                    </p>
                  </>
                ) : null}
              </div>
            </div>
          </div>
          <div className="menu-container__section">
            <div className="menu-container">
              <a style={{ textDecoration: "none" }} href="/play">
                <div className="menu-item ">
                  <h1>Play Now</h1>
                </div>
              </a>
              <Link style={{ textDecoration: "none" }} to="/about">
                <div className="menu-item">
                  <h1>About</h1>
                </div>
              </Link>
            </div>
          </div>
        </div>
        <div className="terms-container">
          <h3 style={{ color: "yellow" }}>Usage terms</h3>
          <p style={{ color: "white" }}>
            You should read our{" "}
            <Link style={{ color: "yellow" }} to="/terms">
              terms
            </Link>{" "}
            regarding how we process and use data that you send to LIGHT. You
            are accepting these terms by playing the game.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
