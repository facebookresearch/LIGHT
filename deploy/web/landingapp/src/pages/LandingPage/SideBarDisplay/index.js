/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React from "react";

/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import SideBarHeader from "./SideBarHeader";
import CollapsibleBox from "../../../components/CollapsibleBox";
import IconCollapsibleBox from "../../../components/IconCollapsibleBox";

//SiderBar - renders Sidebar for application container player, location, mission, and character info as well as xp, giftxp, and progress
const SideBarDisplay = () => {
  return (
    <div className="sidebar">
      <SideBarHeader />
      <div className={`sidebar-body__container flex flex-col justify-center`}>
        <IconCollapsibleBox title={`You are You`}>
          <p className="persona-text text-white" style={{ fontSize: "14px" }}>
            You are, well, yourself... a wandering soul who has yet to become
            someone in the full LIGHT world. Perhaps you may be granted
            admission by the dungeon master?
          </p>
        </IconCollapsibleBox>
        <CollapsibleBox title="Mission">
          <p className="mission-text text-white">
            Find out how to get to LIGHT, then get in to play.
          </p>
        </CollapsibleBox>
        <CollapsibleBox title="Location">
          <div className="location text-white">
            <h3
              style={{
                textDecoration: "underline",
                backgroundColor: "none",
                marginBottom: "0px",
              }}
            >
              IMPOSSIBLE TAVERN
            </h3>
            The tavern is odd. It almost feels like a dream, as nothing you see
            appears to stay for very long. It's almost hard to focus in here.
            There's a ton of background chatter you can't make out, yet the
            space is almost entirely empty. One thing is certain, this is a
            strange yet suited place to start an adventure. There is nothing of
            interest. You notice a shimmering portal.
          </div>
        </CollapsibleBox>
      </div>
    </div>
  );
};
export default SideBarDisplay;
