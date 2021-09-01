import React, { useState } from "react";

import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";
import "./styles.css";

import { Tooltip } from "react-tippy";
import cx from "classnames";
import { Picker, emojiIndex } from "emoji-mart";
import onClickOutside from "react-onclickoutside";

//CUSTOM COMPONENTS
import ExperienceInfo from "../../../components/ExperienceInfo";
import Logo from "../../../components/Logo/index.js";
import CollapseibleBox from "../../../components/CollapsibleBox";
import IconCollapsibleBox from "../../../components/IconCollapsibleBox";
import GameButton from "../../../components/GameButton";
//Icons
import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";

const EmojiPicker = ({ onBlur, ...props }) => {
  EmojiPicker.handleClickOutside = () => onBlur();
  return <Picker style={{ zIndex: "100" }} {...props} />;
};
const BlurClosingPicker = onClickOutside(EmojiPicker, {
  handleClickOutside: () => EmojiPicker.handleClickOutside,
});

const SideBar = ({
  persona,
  location,
  dataModelHost,
  getEntityId,
  selectedEmoji,
  setSelectedEmoji,
  playerXp,
  playerGiftXp,
  isMobile,
  showDrawer,
}) => {
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);

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
        <ExperienceInfo
          isMobile={isMobile}
          experience={playerXp}
          giftExperience={playerGiftXp}
        />
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
      </div>
      <div className="sidebar-body__container">
        <IconCollapsibleBox
          title={`You are ${persona.prefix} ${persona.name}`}
          showEmojiPicker={showEmojiPicker}
          selectedEmoji={selectedEmoji}
          setShowEmojiPicker={setShowEmojiPicker}
          BlurClosingPicker={BlurClosingPicker}
          setSelectedEmoji={setSelectedEmoji}
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
