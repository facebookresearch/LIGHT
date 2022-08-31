
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";
/* REACT ROUTER */
import { 
    useParams,
 } from "react-router-dom";
/* CUSTOM COMPONENTS */
//SECTIONS
import Details from "../EditWorldSections/Details";
import Characters from "../EditWorldSections/Characters";
import Objects from "../EditWorldSections/Objects";
import Quests from "../EditWorldSections/Quests";
import Rooms from "../EditWorldSections/Rooms";
import Interactions from "../EditWorldSections/Interactions";

const WorldEditBody = ()=> {
    let { worldId, categories } = useParams();

    switch(categories) {
        case "details":
            return <Details/>
        case "rooms":
            return <Rooms/>
        case "characters":
            return <Characters/>
        case "quests":
            return <Quests/>
        case "objects":
            return <Objects/>
        case "interactions":
            return <Interactions/>
        default:
            return <Details/>
      }
}

export default WorldEditBody;