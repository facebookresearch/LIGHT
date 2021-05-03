import React from "react";

import "../styles.css";

const Actions = (props) => {
  return (
    <div className="actions-container">
      <h1>Actions</h1>
      <p>
        Look: First things first, to look around you type “look”; this will tell
        you where you are and what’s in the room.
      </p>
      <p>
        Moving: you can take the path to the east in the example above by typing
        “go east” or just “east” or even “e” for short:
      </p>
      <p>
        Examining: you can examine in further detail other characters or objects
        in the game.
      </p>
      <p>
        Picking up objects: you can pick up an object using the verb “get” or
        “pick up”
      </p>
      <p>
        Dropping objects: then of course, you can also put them back down again.
      </p>
      <p>
        Putting objects in containers: you can also put things inside other
        things, and get them out. Examine the container to see what’s inside it.
      </p>
      <p>
        Using objects: you can also use an object with another object, e.g. “use
        fishing rod with pond”.
      </p>
      <p>
        Wear / Wield/ Remove: you can wear clothing items, and wield objects as
        weapons, and use the verb “remove” to take off clothes or stop wielding
        weapons.
      </p>
      <p>Eat / drink: you can eat and drink things, good for more energy!</p>
      <p>
        Give / steal: you can give objects to other characters, or if you are
        really bad try and steal them from others!
      </p>
      <p>
        Trading: instead of trying to steal something, which is very naughty
        isn’t it, you can attempt to trade instead. This is usually done by
        first pointing to what you want to trade and maybe asking them about it:
      </p>
      <p>
        Following someone: you can follow someone by using the “follow” action
        (note: you can stop following them with the “unfollow” action):
      </p>
      <p>
        Fighting!: finally, not always advised, but if you want to fight someone
        you can use the “hit” or “attack” actions. Note you can also attempt to
        “*block”* them from moving with the block action.
      </p>
    </div>
  );
};

export default Actions;
