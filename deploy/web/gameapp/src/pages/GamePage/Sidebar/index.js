/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { updateEmoji } from "../../../features/playerInfo/emoji-slice";
import {
  updateSelectedTip,
  updateInHelpMode,
} from "../../../features/tutorials/tutorials-slice";
/* TOOLTIPS */
import { Tooltip } from "react-tippy";
/* EMOJI PICKER AND LIBRARIES */
import "emoji-mart/css/emoji-mart.css";
/* STYLES */
import "./styles.css";
import cx from "classnames";
/* CUSTOM COMPONENTS */
import SideBarHeader from "./SideBarHeader";
import CollapsibleBox from "../../../components/CollapsibleBox";
import IconCollapsibleBox from "../../../components/IconCollapsibleBox";
import GameButton from "../../../components/GameButton";
import IconButton from "../../../components/IconButtons/InfoButton";
import TutorialPopover from "../../../components/TutorialPopover";

//SiderBar - renders Sidebar for application container player, location, mission, and character info as well as xp, giftxp, and progress
const SideBar = ({ dataModelHost, getEntityId, showDrawer }) => {
  /* LOCAL STATE */
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  /* ----REDUX STATE---- */
  //IsMobile
  const isMobile = useAppSelector((state) => state.view.isMobile);
  //PERSONA
  const persona = useAppSelector((state) => state.persona);
  //LOCATION
  const location = useAppSelector((state) => state.location);
  //EMOJI
  const selectedEmoji = useAppSelector((state) => state.emoji.selectedEmoji);
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setEmoji = (emoji) => {
    dispatch(updateEmoji(emoji));
  };
  const setSelectedTip = (tipNumber) => {
    if (inHelpMode) {
      dispatch(updateSelectedTip(tipNumber));
    }
  };

  return (
    <div className={"sidebar"}>
      <TutorialPopover
        tipNumber={1}
        open={inHelpMode && selectedTip === 1}
        position="right"
      >
        <SideBarHeader />
      </TutorialPopover>
      <div
        className={cx("icon", { editing: showEmojiPicker })}
        style={{ cursor: "pointer" }}
      >
        {dataModelHost && (
          <Tooltip
            style={{ position: "absolute", bottom: 0, right: 5 }}
            title={`suggest changes for ${persona.name}`}
            position="bottom"
          >
            <a
              className="data-model-deep-link"
              href={`${dataModelHost}/edit/${getEntityId(persona.id)}`}
              rel="noopener noreferrer"
              target="_blank"
            >
              <i className="fa fa-edit" aria-hidden="true" />
            </a>
          </Tooltip>
        )}
      </div>
      <div className={`sidebar-body__container ${isMobile ? "mobile" : ""}`}>
        <IconCollapsibleBox
          title={`You are ${persona.prefix} ${persona.name}`}
          showEmojiPicker={showEmojiPicker}
          selectedEmoji={selectedEmoji}
          setShowEmojiPicker={setShowEmojiPicker}
          setSelectedEmoji={setEmoji}
          onClickFunction={() => setSelectedTip(2)}
        >
          <p className="persona-text" style={{ fontSize: "14px" }}>
            <TutorialPopover
              tipNumber={2}
              open={inHelpMode && selectedTip === 2}
              position={isMobile ? "top" : "right"}
            >
              {persona.description.slice(
                0,
                persona.description.indexOf("Your Mission:")
              )}
            </TutorialPopover>
          </p>
        </IconCollapsibleBox>
        <CollapsibleBox
          title="Mission"
          onClickFunction={() => setSelectedTip(3)}
        >
          {
            <p className="mission-text text-white">
              <TutorialPopover
                tipNumber={3}
                open={inHelpMode && selectedTip === 3}
                osition={isMobile ? "top" : "right"}
              >
                {persona.description.slice(
                  persona.description.indexOf(":") + 1,
                  persona.description.length
                )}
              </TutorialPopover>
            </p>
          }
        </CollapsibleBox>
        {location ? (
          <CollapsibleBox
            title="Location"
            onClickFunction={() => setSelectedTip(4)}
          >
            <div className="location text-white">
              <h3
                style={{
                  textDecoration: "underline",
                  backgroundColor: "none",
                  marginBottom: "0px",
                }}
              >
                <TutorialPopover
                  tipNumber={4}
                  open={inHelpMode && selectedTip === 4}
                  position={isMobile ? "top" : "right"}
                >
                  {location.name ? location.name.toUpperCase() : null}
                </TutorialPopover>
              </h3>
              {location.description.split("\n").map((para, idx) => (
                <p key={idx}>{para}</p>
              ))}
              {dataModelHost && (
                <Tooltip
                  style={{ position: "absolute", bottom: 0, right: 5 }}
                  title={`suggest changes for ${
                    location.name.split(" the ")[1]
                  }`}
                  position="bottom"
                >
                  <a
                    className="data-model-deep-link"
                    href={`${dataModelHost}/edit/${getEntityId(location.id)}`}
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <i className="fa fa-edit" aria-hidden="true" />
                  </a>
                </Tooltip>
              )}
            </div>
          </CollapsibleBox>
        ) : null}
      </div>
    </div>
  );
};
export default SideBar;
