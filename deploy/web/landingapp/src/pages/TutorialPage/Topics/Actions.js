/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import "../styles.css";

//IMAGES
import ActionLook from "../../../assets/images/screenshots/Tutorial/Actions/ActionLook.png";
import ActionMoving from "../../../assets/images/screenshots/Tutorial/Actions/ActionMoving.png";
import ActionExamine from "../../../assets/images/screenshots/Tutorial/Actions/ActionExamine.png";
import ActionPickUp from "../../../assets/images/screenshots/Tutorial/Actions/ActionPickUp.png";
import ActionDrop from "../../../assets/images/screenshots/Tutorial/Actions/ActionDrop.png";
import ActionPut from "../../../assets/images/screenshots/Tutorial/Actions/ActionPut.png";
import ActionWearWieldRemove from "../../../assets/images/screenshots/Tutorial/Actions/ActionWearWieldRemove.png";
import ActionEat from "../../../assets/images/screenshots/Tutorial/Actions/ActionEat.png";
import ActionGiveSteal from "../../../assets/images/screenshots/Tutorial/Actions/ActionGiveSteal.png";
import ActionTrade from "../../../assets/images/screenshots/Tutorial/Actions/ActionTrade.png";
import ActionFollow from "../../../assets/images/screenshots/Tutorial/Actions/ActionFollow.png";
import ActionFight from "../../../assets/images/screenshots/Tutorial/Actions/ActionFight.png";

const Actions = (props) => {
  return (
    <div className="actions-container">
      <h1 className="tutorial-header">Actions</h1>
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Look: </span>First things first,
        to look around you type “look”; this will tell you where you are and
        what’s in the room.
      </p>
      <img className="tutorialpage-image__75" src={ActionMoving} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Moving: </span>you can take the
        path to the east in the example above by typing “go east” or just “east”
        or even “e” for short:
      </p>
      <img className="tutorialpage-image__75" src={ActionLook} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Examining: </span>you can examine
        in further detail other characters or objects in the game.
      </p>
      <img className="tutorialpage-image__75" src={ActionExamine} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Picking up objects: </span>you
        can pick up an object using the verb “get” or “pick up”
      </p>
      <img className="tutorialpage-image__75" src={ActionPickUp} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Dropping objects: </span>then of
        course, you can also put them back down again.
      </p>
      <img className="tutorialpage-image__75" src={ActionDrop} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>
          Putting objects in containers:{" "}
        </span>
        you can also put things inside other things, and get them out. Examine
        the container to see what’s inside it.
      </p>
      <img className="tutorialpage-image__75" src={ActionPut} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Using objects: </span>you can
        also use an object with another object, e.g. “use fishing rod with
        pond”.
      </p>
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Wear / Wield/ Remove: </span>you
        can wear clothing items, and wield objects as weapons, and use the verb
        “remove” to take off clothes or stop wielding weapons.
      </p>
      <img className="tutorialpage-image__75" src={ActionWearWieldRemove} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Eat / drink: </span>you can eat
        and drink things, good for more energy!
      </p>
      <img className="tutorialpage-image__75" src={ActionEat} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Give / steal: </span>you can give
        objects to other characters, or if you are really bad try and steal them
        from others!
      </p>
      <img className="tutorialpage-image__75" src={ActionGiveSteal} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Trading: </span>instead of trying
        to steal something, which is very naughty isn’t it, you can attempt to
        trade instead. This is usually done by first pointing to what you want
        to trade and maybe asking them about it:
      </p>
      <img className="tutorialpage-image__75" src={ActionTrade} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Following someone: </span>you can
        follow someone by using the “follow” action (note: you can stop
        following them with the “unfollow” action):
      </p>
      <img className="tutorialpage-image__75" src={ActionFollow} />
      <p className="tutorial-text">
        <span style={{ fontWeight: "bolder" }}>Fighting!: </span>finally, not
        always advised, but if you want to fight someone you can use the “hit”
        or “attack” actions. Note you can also attempt to
        <span style={{ fontWeight: "bolder" }}> “block”</span> them from moving
        with the block action.
      </p>
      <img
        className="tutorialpage-image__75"
        alt="Fight Chat Screenshot"
        src={ActionFight}
      />

      <p className="tutorial-text">
        You now know all you need about LIGHT to play. Click below when you are
        ready:
      </p>
    </div>
  );
};

export default Actions;
