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

  /*---------------HANDLERS----------------*/

  /*---------------HELPERS----------------*/

  /* ----------TAILWIND CLASSES--------- */
  const classNames = {
    chatbarContainer: "flex flex-row w-full border-4 rounded border-green-400",
    chatbar: "flex flex-row",
  };

  return (
    <div>
      <input
        type=""
        name="chat"
        id="chat"
        className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
        placeholder={`${"say"} something`}
      />
    </div>
  );
};

export default ChatInput;
