/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
import ChatButtons from "./ChatButtons";
import ChatInput from "./ChatInput";
import SendButton from "./SendButton";
import TutorialPopover from "../../../../../components/TutorialPopover";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatBar = ({ onSubmit, scrollToBottom, resetIdleTimer }) => {
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
    <div className="_chat-bar_ w-full rounded border-accent border-2 p-2">
      <div className="flex flex-row items-stretch h-[45px]">
        <div className="flex-0">
          <ChatButtons />
        </div>
        <div className="flex-1 flex items-center">
          <ChatInput
            resetIdleTimer={resetIdleTimer}
            onSubmit={chatSubmissionHandler}
          />
        </div>
        <div className="flex-0 flex items-center">
          <SendButton
            resetIdleTimer={resetIdleTimer}
            scrollToBottom={scrollToBottom}
            onSubmit={onSubmit}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatBar;

// <div className={classNames.chatbarContainer}>
// <form onSubmit={chatSubmissionHandler}>
//   <div className={classNames.chatbar}>
//     <div
//       className={`chatbox-button ${
//         tellTarget !== "" ? "tell" : isSaying ? "say" : "do"
//       } ${inHelpMode ? "active" : ""}`}
//       onClick={(e) => {
//         e.preventDefault();
//         if (inHelpMode) {
//           setSelectedTip(5);
//         } else {
//           toggleIsSaying();
//         }
//       }}
//     >
//       {tellTarget !== ""
//         ? `TELL ${formatTellTargetForButton(tellTarget)}`
//         : isSaying
//         ? "SAY"
//         : "DO"}
//       <TutorialPopover
//         tipNumber={5}
//         open={inHelpMode && selectedTip === 5}
//         position="right"
//       ></TutorialPopover>
//     </div>
//     <TutorialPopover
//       tipNumber={6}
//       open={inHelpMode && selectedTip === 6}
//       position="top"
//     >
//       <input
//         className={`chatbox-input ${inHelpMode ? "active" : ""}`}
//         value={chatText}
//         onClick={(e) => {
//           e.preventDefault();
//           if (inHelpMode) {
//             setSelectedTip(6);
//           }
//         }}
//         onChange={(e) => {
//           resetIdleTimer();
//           dispatch(updateChatText(e.target.value));
//         }}
//         onKeyDown={(e) => {
//           if (e.key == "`") {
//             e.preventDefault();
//             toggleIsSaying();
//           }
//           if (e.key == "ArrowUp") {
//             e.preventDefault();
//             if (inHelpMode) {
//               console.log(" HELP MODE ARROW UP KEY PRESS");
//               let nextTip = selectedTip + 1;
//               if (nextTip > 8) {
//                 nextTip = 0;
//               }
//               console.log("TIP CYCLE", nextTip);
//               setSelectedTip(nextTip);
//             } else {
//               if (submittedMessages.length > 0) {
//                 let updatedPosition = cycleMessagesPosition - 1;
//                 if (updatedPosition < 0) {
//                   updatedPosition = submittedMessages.length;
//                 }
//                 setCycleMessagesPosition(updatedPosition);
//                 dispatch(
//                   updateChatText(submittedMessages[updatedPosition])
//                 );
//               }
//             }
//           }
//           if (e.key == "ArrowDown") {
//             e.preventDefault();
//             if (inHelpMode) {
//               let lastTip = selectedTip - 1;
//               if (lastTip < 0) {
//                 lastTip = 8;
//               }
//               setSelectedTip(lastTip);
//             } else {
//               if (submittedMessages.length > 0) {
//                 let updatedPosition = cycleMessagesPosition + 1;
//                 if (updatedPosition >= submittedMessages.length) {
//                   updatedPosition = 0;
//                 }
//                 setCycleMessagesPosition(updatedPosition);
//                 dispatch(
//                   updateChatText(submittedMessages[updatedPosition])
//                 );
//               }
//             }
//           }
//           if (e.key === "Enter" && e.shiftKey) {
//             const prefix = e.target.value.startsWith('"') ? "" : '"';
//             const suffix = e.target.value.endsWith('"') ? "" : '"';
//             dispatch(
//               updateChatText(`${prefix} e.target.value ${suffix}`)
//             );
//           }
//         }}
//         placeholder={
//           isSaying
//             ? "Enter what you wish to say."
//             : "Enter what you wish to do here."
//         }
//       />
//     </TutorialPopover>
//   </div>
//   <div
//     className="chatbox-button send"
//     onClick={inHelpMode ? () => setSelectedTip(7) : chatSubmissionHandler}
//   >
//     <TutorialPopover
//       tipNumber={7}
//       open={inHelpMode && selectedTip === 7}
//       position="left"
//     ></TutorialPopover>
//     SEND
//   </div>
// </form>
// </div>
