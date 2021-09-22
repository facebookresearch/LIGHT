/* REACT */
import React, { useState } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { updateSelectedTip } from "../../features/tutorials/tutorials-slice";
/* ICONS */
import { BiWindow } from "react-icons/bi";
import { FaWindowMinimize } from "react-icons/fa";
/* EMOJI */
import { Picker } from "emoji-mart";
import onClickOutside from "react-onclickoutside";
/* STYLES */
import "./styles.css";
import cx from "classnames";

//IconCollapsibleBox - Renders collapsible container with selectible icon in header.
const IconCollapsibleBox = ({
  showEmojiPicker,
  setSelectedEmoji,
  setShowEmojiPicker,
  selectedEmoji,
  title,
  titleBg,
  containerBg,
  onClickFunction,
  children,
}) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    dispatch(updateSelectedTip(tipNumber));
  };
  /* LOCAL STATE */
  const [isCollapsed, setIsCollapsed] = useState(false);
  const openHandler = () => setIsCollapsed(false);
  const closeHandler = () => setIsCollapsed(true);

  const EmojiPicker = ({ onBlur, ...props }) => {
    EmojiPicker.handleClickOutside = () => onBlur();
    return <Picker style={{ zIndex: "100" }} {...props} />;
  };

  const BlurClosingPicker = onClickOutside(EmojiPicker, {
    handleClickOutside: () => EmojiPicker.handleClickOutside,
  });

  return (
    <div className={`collapsible-container__icon`} onClick={onClickFunction}>
      <div className={`collapsible-box__icon`}>
        <div
          className={cx("icon", { editing: showEmojiPicker })}
          style={{ cursor: "pointer" }}
        >
          <div className="overlay">edit</div>
          <span
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
        <div className={`content-container ${inHelpMode ? "active" : ""} `}>
          <div
            className={`collapsible-header`}
            style={{
              backgroundColor: titleBg,
              borderRadius: isCollapsed ? "15px" : null,
            }}
          >
            <div />
            <h5 className="collapsible-header--text">{title}</h5>
            <div className="collapsible-header--icon">
              {isCollapsed ? (
                <BiWindow style={{}} onClick={openHandler} />
              ) : (
                <FaWindowMinimize onClick={closeHandler} />
              )}
            </div>
          </div>
          <div />
          {isCollapsed ? null : (
            <div
              className={`collapsible-body`}
              style={{ backgroundColor: containerBg, animation: null }}
            >
              {children}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IconCollapsibleBox;
