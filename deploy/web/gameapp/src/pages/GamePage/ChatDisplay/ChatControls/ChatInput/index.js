/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../features/tutorials/tutorials-slice";
/* ---- REDUCER ACTIONS ---- */
import {
  updateChatText,
  updateIsSaying,
  updateTellTarget,
  updateSubmittedMessages,
} from "../../../../../features/chatInput/chatinput-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../components/TutorialPopover";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatInput = ({ onSubmit, scrollToBottom, resetIdleTimer }) => {
  /* ------ REDUX STATE ------ */
  // VIEW STATE
  const isMobile = useAppSelector((state) => state.view.isMobile);
  // CHAT STATE
  const chatText = useAppSelector((state) => state.chatInput.chatText);
  const isSaying = useAppSelector((state) => state.chatInput.isSaying);
  const tellTarget = useAppSelector((state) => state.chatInput.tellTarget);
  const submittedMessages = useAppSelector(
    (state) => state.chatInput.submittedMessages
  );
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    if (inHelpMode) {
      dispatch(updateSelectedTip(tipNumber));
    }
  };
  /*---------------LOCAL STATE----------------*/
  const [cycleMessagesPosition, setCycleMessagesPosition] = useState(0);
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    setCycleMessagesPosition(submittedMessages.length);
  }, [submittedMessages]);

  /*---------------HANDLERS----------------*/
  const toggleIsSaying = () => {
    if (tellTarget) {
      dispatch(updateTellTarget(""));
      dispatch(updateIsSaying(true));
    } else {
      let toggledValue = !isSaying;
      dispatch(updateIsSaying(toggledValue));
    }
  };
  const chatSubmissionHandler = (e) => {
    e.preventDefault();

    if (!inHelpMode) {
      let textSubmission;
      if (!!chatText) {
        if (tellTarget !== "") {
          textSubmission = `tell ${tellTarget} "${chatText}"`;
        } else if (isSaying) {
          textSubmission = `"${chatText}"`;
        } else {
          textSubmission = chatText;
        }
        dispatch(updateSubmittedMessages(chatText));
        onSubmit(textSubmission);
        dispatch(updateChatText(""));
        scrollToBottom();
      }
    }
  };

  /*---------------HELPERS----------------*/
  const formatTellTargetForButton = (str) => {
    let formattedTellTargetName = str.toUpperCase();
    if (str.length > 7) {
      formattedTellTargetName = ` ${formattedTellTargetName.slice(0, 7)}...`;
      if (isMobile) {
        formattedTellTargetName = ` ${formattedTellTargetName.slice(0, 4)}...`;
      }
    }
    return formattedTellTargetName;
  };

  return (
    <div className="_chatbar-container bg-transparent m-6 border-teal-400 border-2 p-2 rounded">
      <form className="flex justify-between" onSubmit={chatSubmissionHandler}>
        <div className="_chatbar flex w-full">
          <div
            className={`_chatbox-button btn btn-${
              tellTarget !== "" ? "warning" : isSaying ? "primary" : "secondary"
            } ${inHelpMode ? "active" : ""}`}
            onClick={(e) => {
              e.preventDefault();
              if (inHelpMode) {
                setSelectedTip(5);
              } else {
                toggleIsSaying();
              }
            }}
          >
            {tellTarget !== ""
              ? `TELL ${formatTellTargetForButton(tellTarget)}`
              : isSaying
              ? "SAY"
              : "DO"}
            <TutorialPopover
              tipNumber={5}
              open={inHelpMode && selectedTip === 5}
              position="right"
            ></TutorialPopover>
          </div>
          <TutorialPopover
            tipNumber={6}
            open={inHelpMode && selectedTip === 6}
            position="top"
          >
            <input
              className={`w-full bg-transparent border-none _chatbox-input ${inHelpMode ? "active" : ""}`}
              value={chatText}
              onClick={(e) => {
                e.preventDefault();
                if (inHelpMode) {
                  setSelectedTip(6);
                }
              }}
              onChange={(e) => {
                resetIdleTimer();
                dispatch(updateChatText(e.target.value));
              }}
              onKeyDown={(e) => {
                if (e.key == "`") {
                  e.preventDefault();
                  toggleIsSaying();
                }
                if (e.key == "ArrowUp") {
                  e.preventDefault();
                  if (inHelpMode) {
                    console.log(" HELP MODE ARROW UP KEY PRESS");
                    let nextTip = selectedTip + 1;
                    if (nextTip > 8) {
                      nextTip = 0;
                    }
                    console.log("TIP cylce", nextTip);
                    setSelectedTip(nextTip);
                  } else {
                    if (submittedMessages.length > 0) {
                      let updatedPosition = cycleMessagesPosition - 1;
                      if (updatedPosition < 0) {
                        updatedPosition = submittedMessages.length;
                      }
                      setCycleMessagesPosition(updatedPosition);
                      dispatch(
                        updateChatText(submittedMessages[updatedPosition])
                      );
                    }
                  }
                }
                if (e.key == "ArrowDown") {
                  e.preventDefault();
                  if (inHelpMode) {
                    let lastTip = selectedTip - 1;
                    if (lastTip < 0) {
                      lastTip = 8;
                    }
                    setSelectedTip(lastTip);
                  } else {
                    if (submittedMessages.length > 0) {
                      let updatedPosition = cycleMessagesPosition + 1;
                      if (updatedPosition >= submittedMessages.length) {
                        updatedPosition = 0;
                      }
                      setCycleMessagesPosition(updatedPosition);
                      dispatch(
                        updateChatText(submittedMessages[updatedPosition])
                      );
                    }
                  }
                }
                if (e.key === "Enter" && e.shiftKey) {
                  const prefix = e.target.value.startsWith('"') ? "" : '"';
                  const suffix = e.target.value.endsWith('"') ? "" : '"';
                  dispatch(
                    updateChatText(`${prefix} e.target.value ${suffix}`)
                  );
                }
              }}
              placeholder={
                isSaying
                  ? "Enter what you wish to say."
                  : "Enter what you wish to do here."
              }
            />
          </TutorialPopover>
        </div>
        <div
          className="btn btn-ghost text-teal-500 _chatbox-button _send"
          onClick={inHelpMode ? () => setSelectedTip(7) : chatSubmissionHandler}
        >
          <TutorialPopover
            tipNumber={7}
            open={inHelpMode && selectedTip === 7}
            position="left"
          ></TutorialPopover>
          Send
        </div>
      </form>
    </div>
  );
};

export default ChatInput;
