/* REACT */
import React, { useEffect, useCallback, useRef } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { updateSelectedTip } from "../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import ActionBar from "./ActionBar";
import ChatMessages from "./ChatMessages";
import ChatControls from "./ChatControls";
import TutorialPopover from "../../../components/TutorialPopover";
/* UTILS */
import { setCaretPosition } from "../../../utils";

//ChatDisplay - renders primary container for both chat and entirety of chat controls
const ChatDisplay = ({
  messages,
  onSubmit,
  agents,
  getDataModelAddress,
  getLocationState,
  idle,
  resetIdleTimer,
}) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  //XP
  const xp = useAppSelector((state) => state.xp.value);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    dispatch(updateSelectedTip(tipNumber));
  };
  /*---------------REFS----------------*/
  const chatContainerRef = useRef(null);
  /*---------------UT----------------*/
  const getAgentName = (agent) => (agents ? agents[agent] : agent);
  const getEntityId = (agent) => agent.match(/\d+$/)[0];
  const dataModelHost = getDataModelAddress();
  /*---------------CALLBACKS----------------*/
  const scrollToBottom = useCallback(
    () =>
      setTimeout(() => {
        if (chatContainerRef.current)
          chatContainerRef.current.scrollTop =
            chatContainerRef.current.scrollHeight;
      }, 0),
    [chatContainerRef]
  );
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    scrollToBottom();
  }, [scrollToBottom, messages]);
  /* ----------TAILWIND CLASSES--------- */
  const classNames = {
    chatWrapper:
      " w-full h-full bg-indigo-900 bg-opacity-50 	overflow-y-hidden ",
    chat: "flex flex-col w-full h-4/5 overflow-y-scroll",
  };
  const { presentAgents } = getLocationState(messages);
  return (
    <div className="h-screen">
      <div className="h-14">
        <ActionBar
          presentAgents={presentAgents}
          getAgentName={getAgentName}
          getEntityId={getEntityId}
          dataModelHost={dataModelHost}
        />
      </div>
      <div className={classNames.chatWrapper}>
        <div className={classNames.chat} ref={chatContainerRef}>
          <ChatMessages messages={messages} />
        </div>
        <div className="h-1/5">
          <ChatControls
            onSubmit={onSubmit}
            presentAgents={presentAgents}
            getAgentName={getAgentName}
            getEntityId={getEntityId}
            dataModelHost={dataModelHost}
            scrollToBottom={scrollToBottom}
            idle={idle}
            resetIdleTimer={resetIdleTimer}
          />
          <div className="flex justify-end">
            <p className=" text-gray-200">XP earned this scene:{xp}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatDisplay;
