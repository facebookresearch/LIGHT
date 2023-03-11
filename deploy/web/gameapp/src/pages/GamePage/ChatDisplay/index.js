/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useEffect, useState, useCallback, useRef } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
import { updateSelectedTip } from "../../../features/tutorials/tutorials-slice";
/* STYLES */
import "./styles.css";
/* CUSTOM COMPONENTS */
import ActionBar from "./ActionBar";
import ChatMessages from "./ChatMessages";
import ChatControls from "./ChatControls";
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
  chatInputRef,
  showCommandHelp
}) => {
  /* ----REDUX STATE---- */
  //TUTORIAL;
  const inHelpMode = useAppSelector((state) => state.tutorials.inHelpMode);
  const selectedTip = useAppSelector((state) => state.tutorials.selectedTip);
  const persona = useAppSelector((state) => state.persona);
  //PLAYER XP STATE
  const xp = useAppSelector((state) => state.xp.value);
  //SESSION XP STATE
  const sessionXp = useAppSelector((state) => state.sessionXp.value);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  const setSelectedTip = (tipNumber) => {
    dispatch(updateSelectedTip(tipNumber));
  };
  /* LOCAL STATE */
  const [nonPlayerAgents, setNonPlayerAgents] = useState([]);
  const [chatPosition, setChatPosition] = useState(0);
  const [chatBottom, setChatBottom] = useState(0);
  const [showScrollBottomButton, setShowScrollBottomButton] = useState(false);
  const [unseenNewMessages, setUnseenNewMessages] = useState(false);
  /*---------------REFS----------------*/
  const chatContainerRef = useRef(null);

  /*---------------UT----------------*/
  const getAgentName = (agent) => (agents ? agents[agent] : agent);
  const getEntityId = (agent) => agent.match(/\d+$/)[0];
  const dataModelHost = getDataModelAddress();
  /*---------------CALLBACKS----------------*/
  const scrollTracker = ()=>{
    if(chatContainerRef.current){
      setChatPosition(chatContainerRef.current.scrollTop);
    }
  }

  const scrollToBottom = useCallback(
    () =>
      setTimeout(() => {
        console.log("CHAT DISPLAY SCROLL REF INFO:",showScrollBottomButton,  "HEIGHT:  ", chatContainerRef.current.scrollHeight , "SCROLLTOP:  ", chatContainerRef.current.scrollTop)
        if(!showScrollBottomButton){
          if(chatContainerRef.current ){
            let updatedBottom = chatContainerRef.current.scrollHeight;
            chatContainerRef.current.scrollTop = updatedBottom;
            let updatedCurrentPosition = chatContainerRef.current.scrollTop

            setChatPosition(updatedCurrentPosition);
            setChatBottom(updatedCurrentPosition)
          }
        }
      }, 0),
    [chatContainerRef]
  );
  /*---------------LIFECYCLE----------------*/
  useEffect(() => {
    if(!showScrollBottomButton){
      scrollToBottom();
    }else{
      setUnseenNewMessages(true);
    }
  }, [messages]);

  useEffect(() => {
    console.log("CHAT POSITION:  ", chatPosition, "CHAT BOTTOM:  ",chatBottom, chatContainerRef.current.scrollHeight, "CHATREF:  ", chatContainerRef.current)
      if(chatPosition > chatBottom-60){
        setShowScrollBottomButton(false)
      }else{
        setShowScrollBottomButton(true)
      }
  }, [chatPosition])

  useEffect(() => {
    if( !showScrollBottomButton && unseenNewMessages){
      setUnseenNewMessages(false)
    }
  }, [showScrollBottomButton])

  useEffect(() => {
    const { presentAgents } = getLocationState(messages);
    let updatedNonPlayerAgents = presentAgents.filter(
      (id) => id !== persona.id
    ); // only show users other than self
    setNonPlayerAgents(updatedNonPlayerAgents);
  }, [messages]);
  /* ----------TAILWIND CLASSES--------- */

  const { presentAgents } = getLocationState(messages);
  return (
    <div className="_chatdisplay-container_ w-full h-full flex flex-col ">
      {showCommandHelp ? 
        <div className = "w-full border-2 border-accent border-solid" >
          <p className={"text-white font-bold"}>
            HELP COMMAND LOGIC GOES HERE
          </p>
        </div>
      :null
    }
      {nonPlayerAgents.length ? (
        <div className="_actionbar-container_ flex-0 pt-4 mb-4">
          <ActionBar
            presentAgents={nonPlayerAgents}
            getAgentName={getAgentName}
            getEntityId={getEntityId}
            dataModelHost={dataModelHost}
            chatInputRef={chatInputRef}
          />
        </div>
      ) : null}
      <div className=" _chatdisplay-chat-container_ w-full flex flex-1 flex-col h-full bg-indigo-900 bg-opacity-50 overflow-hidden p-7 rounded-t-md">
        <div
          className="_chatdisplay-message-container_ max-w-full sm:w-full md:max-w-full flex-1 grow-[5] overflow-y-scroll"
          onScroll={scrollTracker}
          ref={chatContainerRef}
        >
          <ChatMessages
            messages={messages}
            scrollToBottom={scrollToBottom}
            chatInputRef={chatInputRef}
          />
        </div>
        <div className="_scroll-button-container_ flex w-full justify-center items-center bg-opacity-0">
        { showScrollBottomButton ?
          <div onClick={()=>scrollToBottom()} className={`_scroll-button_ ${unseenNewMessages ? "new-message" : ""} border-2 text-white border-white text-xs rounded m-2 p-2`}>
            SCROLL TO BOTTOM 
          </div>:
          null
        }
        </div>
        <div className="__chatdisplay-chatcontrols-container__  flex-none md:h-[120px]">
          <ChatControls
            onSubmit={onSubmit}
            presentAgents={presentAgents}
            getAgentName={getAgentName}
            getEntityId={getEntityId}
            dataModelHost={dataModelHost}
            scrollToBottom={scrollToBottom}
            idle={idle}
            resetIdleTimer={resetIdleTimer}
            chatInputRef={chatInputRef}
            autoScrollToBottom={!showScrollBottomButton}
          />
          <div className="flex justify-end">
            <p className="text-base-100 opacity-80 mt-2 text-xs">
              XP earned in this scene:{" "}
              <strong className="text-warning">{sessionXp}</strong>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatDisplay;
