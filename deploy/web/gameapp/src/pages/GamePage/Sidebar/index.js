import React, { useState } from "react";

import "react-tippy/dist/tippy.css";
import "emoji-mart/css/emoji-mart.css";
import "./styles.css";

import { Tooltip } from "react-tippy";
import cx from "classnames";
import { Picker, emojiIndex } from "emoji-mart";
import onClickOutside from "react-onclickoutside";

//CUSTOM COMPONENTS
import CollapseibleBox from "../../../components/CollapsibleBox";

//Icons
import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";

const EmojiPicker = ({ onBlur, ...props }) => {
  EmojiPicker.handleClickOutside = () => onBlur();
  return <Picker {...props} />;
};
const BlurClosingPicker = onClickOutside(EmojiPicker, {
  handleClickOutside: () => EmojiPicker.handleClickOutside,
});

const SideBar = ({ persona, location, dataModelHost, getEntityId }) => {
  const defaultEmoji = "❓";
  const [showCharacter, setShowCharacter] = useState(true);
  const [showEmojiPicker, setShowEmojiPicker] = React.useState(false);
  const [selectedEmoji, setSelectedEmoji] = React.useState(defaultEmoji);

  return (
    <div>
      {persona ? (
        <div className="persona">
          <div
            className={cx("icon", { editing: showEmojiPicker })}
            style={{ cursor: "pointer" }}
          >
            <div className="overlay">edit</div>
            <span
              className="char-icon"
              role="img"
              aria-label="avatar"
              onClick={() => setShowEmojiPicker(true)}
            >
              {selectedEmoji}
            </span>
            {showEmojiPicker ? (
              <div
                style={{
                  position: "absolute",
                  top: "80px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  zIndex: 999,
                }}
              >
                <BlurClosingPicker
                  autoFocus={true}
                  onBlur={() => setShowEmojiPicker(false)}
                  onSelect={(emoji) => {
                    // TODO: Send the selected emoji to the back-end so we can keep record it
                    setSelectedEmoji(emoji.native);
                    setShowEmojiPicker(false);
                  }}
                />
              </div>
            ) : null}
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              alignItems: "center",
              margin: "10px",
            }}
          >
            {showCharacter ? (
              <FaWindowMinimize onClick={() => setShowCharacter(false)} />
            ) : (
              <BiWindow onClick={() => setShowCharacter(true)} />
            )}
          </div>
          <h3
            style={{
              fontFamily: "fantasy",
              fontWeight: "900",
              marginTop: "6px",
              fontSize: "large",
            }}
          >
            You are {persona.prefix} {persona.name}
          </h3>
          {showCharacter ? (
            <p className="persona-text" style={{ fontSize: "14px" }}>
              {persona.description.slice(
                0,
                persona.description.indexOf("Your Mission:")
              )}
            </p>
          ) : (
            <div />
          )}
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
      ) : null}
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
              {location.name.toUpperCase()}
            </h3>
            <p>
              {location.description.split("\n").map((para, idx) => (
                <p key={idx}>{para}</p>
              ))}
            </p>
            {dataModelHost && (
              <Tooltip
                style={{ position: "absolute", bottom: 0, right: 5 }}
                title={`suggest changes for ${location.name.split(" the ")[1]}`}
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
  );
};
export default SideBar;
