
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React, {useState} from "react";
import ReactDOM from "react-dom";
//VIEWS
import Task from "./views/Task";
import Preview from "./views/Preview";

import LoadingScreen from "./components/LoadingScreen";
import { useMephistoTask } from "mephisto-task";
// import { TimesComponent } from "./components/times_component.jsx";
// import { SubmitButton } from "./components/submit_button.jsx";

import "./styles.css";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap-typeahead/css/Typeahead.css';
/* ================= Application Components ================= */

function MainApp() {
  const {
    blockedReason,
    blockedExplanation,
    isPreview,
    isLoading,
    initialTaskData,
    handleSubmit,
  } = useMephistoTask();


  if (blockedReason !== null) {
    return (
      <section className="hero is-medium is-danger">
        <div class="hero-body">
          <h2 className="title is-3">{blockedExplanation}</h2>{" "}
        </div>
      </section>
    );
  }

  if (isPreview) {
    return (
      <div className="view-container">
            <Preview />
      </div>
    );
  }

  // Check if initial task data returns null
  if (isLoading || initialTaskData == null) {
    return <LoadingScreen />;
  }

  // const state = initialTaskData;
  const mephistoData = initialTaskData;

  const active = true;

  const state = {
  }


  //console.log('active? ', active);

  const ObjectDummyData= {
    itemCategory:"objects",
    selection:[
        {
          id:1,
          name:"Sword",
          attributes:[{name:"wieldable",value:true}],
          description: "A normal iron longsword, unscratched, with a comfortable grip."
        },
        {
          id:2,
          name:"Shield",
          attributes:[{name:"armor",value:true}],
          description: "A large metal shield with the crest of the local lord painted and etched on the front."
        },
        {
          id:3,
          name:"Magic Lamp",
          attributes:[],
          description:"An ordinary looking lamp that pulses with potential to the magically attuned."
        },
        {
          id:4,
          name:"Treasure Chest",
          attributes:[{name:"container",value:true}],
          description: "A massive ornate chest over flowing with gold coins and precious gems."
        }
      ]
    }


  const CharacterDummyData= {
    itemCategory:"characters",
    selection:[
          {
            id:1,
            name:"Butcher",
            attributes:[],
            description: "A humble carver and seller of meats."
          },
          {
            id:2,
            name:"Baker",
            attributes:[],
            description: "A talented and thoughtful distributor of baked goods they prepare."
          },
          {
            id:3,
            name:"Candlestick Maker",
            attributes:[],
            description:"A wealthy and arrogant wax sculptor."
          },
          {
            id:4,
            name:"Kroktar Devourer of Souls",
            attributes:[],
            description: "An armor clad, ageless horror who is said to have felled a thousand armies."
          }
        ]
  }

  const LocationDummyData= {
    itemCategory:"locations",
    selection:[
        {
          id:1,
          name:"Smithing Hut",
          attributes:[],
          description: "A blacksmith's workshop laden with tools and at the center is a forge"
        },
        {
          id:2,
          name:"Dungeon",
          attributes:[],
          description: "A castle's windowless dungeon, the walls made of stone, bars line some cells and chains hang from the walls."
        },
        {
          id:3,
          name:"Wizard Tower",
          attributes:[],
          description:"A tall amethyst tower with floating on stones high in the sky, filled with books, artefacts, and presumably a wizard."
        },
        {
          id:4,
          name:"Ice Giant Camp",
          attributes:[],
          description: "A circle of massive tents around a fire the size of an average human's house.  The camp is covered in think layers of icy snow."
        }
      ]
  }

  return (
    <div className="view-container">
      <Task
        data={LocationDummyData}
        handleSubmit={handleSubmit}
        />
    </div>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
