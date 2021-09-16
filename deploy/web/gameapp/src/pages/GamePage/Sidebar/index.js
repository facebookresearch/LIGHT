/* REACT */
import React, { useState } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { updateEmoji } from "../../../features/playerInfo/emoji-slice";
import { updateInHelpMode } from "../../../features/tutorials/tutorials-slice";
/* TOOLTIPS */
import "react-tippy/dist/tippy.css";
import { Tooltip } from "react-tippy";
/* EMOJI PICKER AND LIBRARIES */
import "emoji-mart/css/emoji-mart.css";
/* STYLES */
import "./styles.css";
import cx from "classnames";
/* CUSTOM COMPONENTS */
import ExperienceInfo from "../../../components/ExperienceInfo";
import Logo from "../../../components/Logo/index.js";
import CollapseibleBox from "../../../components/CollapsibleBox";
import IconCollapsibleBox from "../../../components/IconCollapsibleBox";
import GameButton from "../../../components/GameButton";
import IconButton from "../../../components/IconButton";

//SiderBar - renders Sidebar for application container player, location, mission, and character info as well as xp, giftxp, and progress
const SideBar = ({ dataModelHost, getEntityId, isMobile, showDrawer }) => {
  /* LOCAL STATE */
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  /* ----REDUX STATE---- */
  //PERSONA
  const persona = useAppSelector((state) => state.persona);
  //LOCATION
  const location = useAppSelector((state) => state.location);
  //EMOJI
  const selectedEmoji = useAppSelector((state) => state.emoji.selectedEmoji);
  const setEmoji = (emoji) => {
    dispatch(updateEmoji(emoji));
  };
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);

  const toggleHelpMode = () => {
    let helpModeUpdate = !inHelpMode;
    dispatch(updateInHelpMode(helpModeUpdate));
  };

  return (
    <div
      className={
        isMobile
          ? showDrawer
            ? "mobile-sidebar open"
            : "mobile-sidebar"
          : "sidebar"
      }
    >
      <div className="sidebar-header__container">
        {isMobile ? null : <Logo />}
        <ExperienceInfo isMobile={isMobile} />
      </div>
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
      <div className="sidebar-row">
        <a
          href={"/logout"}
          style={{ color: "#0060B6", textDecoration: "none" }}
        >
          <GameButton text={"LOGOUT"} clickFunction={() => {}} />
        </a>
        <IconButton buttonFunction={toggleHelpMode} />
      </div>
      <div className="sidebar-body__container">
        <IconCollapsibleBox
          title={`You are ${persona.prefix} ${persona.name}`}
          showEmojiPicker={showEmojiPicker}
          selectedEmoji={selectedEmoji}
          setShowEmojiPicker={setShowEmojiPicker}
          setSelectedEmoji={setEmoji}
          titleBg={"gold"}
        >
          <p className="persona-text" style={{ fontSize: "14px" }}>
            {persona.description.slice(
              0,
              persona.description.indexOf("Your Mission:")
            )}
          </p>
        </IconCollapsibleBox>
        <CollapseibleBox
          title="Mission"
          titleBg="yellow"
          containerBg="lightyellow"
        >
          {
            <p className="mission-text">
              {persona.description.slice(
                persona.description.indexOf(":") + 1,
                persona.description.length
              )}
            </p>
          }
        </CollapseibleBox>
        {location ? (
          <CollapseibleBox
            title="Location"
            titleBg="#76dada"
            containerBg="#e0fffe"
          >
            <div className="location" style={{ margin: 0 }}>
              <h3
                style={{
                  textDecoration: "underline",
                  backgroundColor: "none",
                  fontFamily: "fantasy",
                }}
              >
                {location.name ? location.name.toUpperCase() : null}
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
          </CollapseibleBox>
        ) : null}
      </div>
    </div>
  );
};
export default SideBar;
