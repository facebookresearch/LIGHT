/* REACT */
import React, { useState, useEffect } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../../../../app/hooks";
import { updateSelectedTip } from "../../../../../../features/tutorials/tutorials-slice";
/* ---- REDUCER ACTIONS ---- */
import {
  updateChatText,
  updateIsSaying,
  updateTellTarget,
  updateSubmittedMessages,
} from "../../../../../../features/chatInput/chatinput-slice";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../components/TutorialPopover";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatInput = ({ onSubmit, scrollToBottom, resetIdleTimer }) => {
  /* ------ REDUX STATE ------ */
  // VIEW STATE
  //   const isMobile = useAppSelector((state) => state.view.isMobile);
  //   // CHAT STATE
  //   const chatText = useAppSelector((state) => state.chatInput.chatText);
  //   const isSaying = useAppSelector((state) => state.chatInput.isSaying);
  //   const tellTarget = useAppSelector((state) => state.chatInput.tellTarget);
  //   const submittedMessages = useAppSelector(
  //     (state) => state.chatInput.submittedMessages
  //   );
  //   //TUTORIAL;
  //   const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  //   const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  //   /* ----REDUX ACTIONS---- */
  //   // REDUX DISPATCH FUNCTION
  //   const dispatch = useAppDispatch();
  //   const setSelectedTip = (tipNumber) => {
  //     if (inHelpMode) {
  //       dispatch(updateSelectedTip(tipNumber));
  //     }
  //   };
  //   /*---------------LOCAL STATE----------------*/
  //   const [cycleMessagesPosition, setCycleMessagesPosition] = useState(0);
  //   /*---------------LIFECYCLE----------------*/
  //   useEffect(() => {
  //     setCycleMessagesPosition(submittedMessages.length);
  //   }, [submittedMessages]);

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

  /*---------------HELPERS----------------*/

  /* ----------TAILWIND CLASSES--------- */
  const classNames = {};
  return (
    <div className=" bg-white inline-flex justify-center items-center min-w-40 ">
      <button
        type="button"
        className=" w-40 absolute  items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-yellow-600 my-3 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
      >
        SEND
      </button>
    </div>
  );
};

export default ChatInput;

// <div
// className="chatbox-button send"
// onClick={
//   inHelpMode ? () => setSelectedTip(7) : chatSubmissionHandler
// }
// >
// <button
// type="button"
// className="chatbox-button send"
// onClick={
// inHelpMode ? () => setSelectedTip(7) : chatSubmissionHandler
// }
// >
// SEND
// </button>
