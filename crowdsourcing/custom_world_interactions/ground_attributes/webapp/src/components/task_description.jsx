/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

function TaskDescription() {
  return (
    <div>
      <div className="title is-3">Objects Interactions Annotation Task</div>
      <p>
        We're trying to crowdsource possible interactions between a set of
        items. These interactions are set in a <b>medieval fantasy scenario</b>,
        and as such should not refer to real people, places, or modern day
        technologies. In this task you will be able to select two objects from a
        randomized list: Primary Object and Secondary Object. If none of the
        objects are compatible, please feel free to use the <i>Other</i> field
        to do the task with a Secondary Object of your choice.
      </p>
      <p>
        After that, write a simple <b>interaction</b> between these two objects
        in the textbox.
      </p>
      <br />
      <p>
        Imagine a character in a medieval fantasy adventure were to try to{" "}
        <b>'Use PRIMARY_OBJECT with SECONDARY_OBJECT'</b>. Narrate the
        interaction to them.
      </p>
      <br />
      <p>
        For example, let's say we have a fire torch as the primary object and a
        wooden table as the target object.
      </p>
      <p>
        In this case, a good action description would be:{" "}
        <i>
          "You light the table on fire with the torch. It ignites and burns to
          the ground, leaving a pile of ash."
        </i>
      </p>
      <br />
      <h2>
        <b>Good Examples:</b>
      </h2>
      <br />
      <div>
        <ul>
          <li>
            <b>Primary:</b> Rusty key. <b>Target:</b> Bucket. <b>Interaction</b>
            :{" "}
            <i>
              You scrape the key on the edge of the bucket. It sounds terrible,
              and leaves a mark.
            </i>
          </li>
          <li>
            <b>Primary:</b> Towel. <b>Target:</b> Rock. <b>Interaction</b>:{" "}
            <i>
              You rub the rock with the towel. The rock is now shiny, but the
              towel could use a cleaning.
            </i>
          </li>
          <li>
            <b>Primary:</b> Rock. <b>Target:</b> Tree. <b>Interaction</b>:{" "}
            <i>
              You throw the rock at the tree. It hits a branch, and a bird flies
              away.
            </i>
          </li>
        </ul>
      </div>
      <br />
      <p>
        Avoid submitting interactions which are physically impossible or
        nonsense in the current scenario. Interactions must also be written in
        second person.
      </p>
      <div>
        <br />
        <h2>
          <b>Bad Examples:</b>
        </h2>
        <br />
        <ul>
          <li>
            <b>Primary:</b> shirt. <b>Target:</b> bucket. <b>Interaction</b>:{" "}
            <i>
              You put the shirt in the bucket and it transforms into a pair of
              pants.
            </i>
          </li>
          <li>
            <b>Bad Reason:</b> This interaction isn't very plausible.
            Interactions don't need to be expected or mundane, but they should
            be a realistic occurrence.
          </li>
          <br />
          <li>
            <b>Primary:</b> Ball. <b>Target:</b> Table. <b>Interaction</b>:{" "}
            <i>The ball rolls off of the table and falls on the floor.</i>
          </li>
          <li>
            <b>Bad Reason:</b> This interaction isn't written in second person.
            The correct format would be "You roll the ball on the table. It
            falls off of the other side onto the floor"
          </li>
          <br />
          <li>
            <b>Primary:</b> Tea. <b>Target:</b> Table. <b>Interaction</b>:{" "}
            <i>
              You put the tea on the table but it falls off, leaving a mark on
              the rug.
            </i>
          </li>
          <li>
            <b>Bad Reason:</b> This interaction uses a third object (Rug). It's
            preferable for the interaction to be generic for any environment,
            therefore not envolving more than the two objects mentioned.
          </li>
          <br />
          <li>
            <b>Primary:</b> Magical Ring. <b>Target:</b> Magician.{" "}
            <b>Interaction</b>:{" "}
            <i>
              You call a magician with your cellphone and he shows up to analyze
              the Magical Ring.
            </i>
          </li>
          <li>
            <b>Bad Reason:</b> Again, this interaction uses a random third
            object (Cellphone). It also uses an object which should not exist in
            the medieval fantasy setting (Cellphone).
          </li>
        </ul>
      </div>
    </div>
  );
}

export { TaskDescription };
