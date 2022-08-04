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
/* STYLES */
import "../styles.css";
/* CUSTOM COMPONENTS */
import TutorialPopover from "../../../../../../components/TutorialPopover";

import { FaSync } from "react-icons/fa";

// ChatInput - Component that renders chat bar along with Say/Do buttons and send button
const ChatButtons = ({ onSubmit, scrollToBottom, resetIdleTimer }) => {
  /* ------ REDUX STATE ------ */
  // VIEW STATE
  //   const isMobile = useAppSelector((state) => state.view.isMobile);
  //   // CHAT STATE
  //   const chatText = useAppSelector((state) => state.chatInput.chatText);
  const isSaying = useAppSelector((state) => state.chatInput.isSaying);
  const tellTarget = useAppSelector((state) => state.chatInput.tellTarget);
  //   const submittedMessages = useAppSelector(
  //     (state) => state.chatInput.submittedMessages
  //   );
  //   //TUTORIAL;
  //   const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  //   const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  //   /* ----REDUX ACTIONS---- */
  //   // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
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
    console.log("TOGGLE BEING CLICKED");
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
    <>
      <button
        onClick={toggleIsSaying}
        type="button"
        className={` w-20 items-start px-1.5 py-0.5 border border-transparent text-lg font-medium rounded shadow-sm text-white ${
          tellTarget
            ? "bg-red-700 "
            : isSaying
            ? "bg-green-700"
            : "bg-blue-500 "
        }`}
      >
        <span className="flex flex-row justify-between items-center">
          {tellTarget ? `TELL ${tellTarget}` : isSaying ? "SAY" : "DO"}
          <FaSync color="white" size={20} />
        </span>
      </button>
    </>
  );
};

export default ChatButtons;

{
  /* <div className="relative ">
<button
  type="button"
  className=" w-40 absolute items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
>
  SAY
</button>
<button
  type="button"
  className=" w-40 absolute  items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-orange-600 my-3 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
>
  DO
</button>
</div> */
}
