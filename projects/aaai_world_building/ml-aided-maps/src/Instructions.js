/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

export default function Instruction() {
  return (
    <div className="instruction">
      <h3>Goal / Motivations</h3>
      <p>
        The goal is to create a realistic, small world of various locations,
        with different characters and objects inside them. The setting is a
        medieval fantasy world.
      </p>
      <p>
        The motivation behind creating such worlds is to create games where
        players will travel from location to location, interact with the
        characters in the location, and interact with the objects inside the
        location.
      </p>

      <p>
        We want to design the best worlds that would be fun for people to play a
        game in, so:
      </p>
      <ol>
        <li>
          we want locations that <strong>logically connect</strong> (example:
          bedrooms are not often next to a zoo, but a bedroom could be next to a
          living room)
        </li>
        <li>
          we want a{" "}
          <strong>diversity of different characters and objects</strong> in the
          locations (example: a chef should be in locations where that makes
          sense, but every location does not need a chef character)
        </li>
      </ol>

      <h3>Instructions</h3>
      <p>
        There will be <strong>three steps</strong> for this task:
      </p>
      <ol>
        <li>
          <strong>Fill Locations</strong> - You will be given a grid of empty
          locations. Use the dropdown menu to decide what should be in each
          location. After you fill all of the locations in the grid, press
          “Submit” and move to step 2.
        </li>
        <li>
          <strong>Fill Characters and Objects</strong> - In each location, you
          will add characters and objects to the location using the dropdown.
          You can add multiple characters and multiple objects to each location.
          After you add characters and objects to the locations, press “Submit”
          and move to step 3.
        </li>
        <li>
          <strong>Fill out a survey about your experience.</strong> Click the
          survey link at the end, fill out all of the questions, and press
          “Submit.”
        </li>
      </ol>

      <div className="example">
        <p>
          Example of a location is: <strong>Kitchen</strong>
        </p>
        <p>
          Example characters inside this location:{" "}
          <strong>Chef, servant</strong>
        </p>
        <p>
          Example objects inside this location:{" "}
          <strong>Brick oven, plates, table</strong>
        </p>
        <p>
          Example of linked locations:{" "}
          <strong>the kitchen is next to the dining room</strong>
        </p>
      </div>

      <p>
        <em>
          <strong>Important Note:</strong> We expect you to rely on your
          personal knowledge. For example, if you have decided to place the
          kitchen and you want to put a character in the room, you can use our
          type ahead feature to search for the character "chef." Another
          example, if you have placed a "town" and a "farm," and you think they
          can be linked with a road or a path, please use our type ahead feature
          in the search bar to find close possibilities.{" "}
          <strong>
            We do not expect you to read the entire drop down menu of options!
          </strong>
        </em>
      </p>
    </div>
  );
}
