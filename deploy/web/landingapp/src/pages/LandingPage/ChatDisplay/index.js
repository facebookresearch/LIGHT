/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useEffect, useState, useCallback, useRef } from "react";
/* STYLES */

/* CUSTOM COMPONENTS */
// import ActionBar from "./ActionBar";
import ChatMessages from "./ChatMessages";
import ChatControls from "./ChatControls";

//ChatDisplay - renders primary container for both chat and entirety of chat controls
const ChatDisplay = ({
  chatInputText,
  inputActionType,
  inputActionTypeToggleHandler,
  inputChangeHandler,
  scrollToBottom,
  messages,
  submittedActions,
  onSubmit,
  chatContainerRef,
}) => {
  return (
    <div className="h-full m-8 flex flex-col">
      {/* {nonPlayerAgents.length ? (
        <div className="flex-0 mb-4">
          <ActionBar
            presentAgents={nonPlayerAgents}
            getAgentName={getAgentName}
            getEntityId={getEntityId}
            dataModelHost={dataModelHost}
          />
        </div>
      ) : null} */}
      <div className="flex flex-1 flex-col h-full bg-indigo-900 bg-opacity-50 overflow-hidden p-7 rounded-t-md">
        <div
          className="flex-1 grow-[5] overflow-y-scroll"
          ref={chatContainerRef}
        >
          <ChatMessages messages={messages} scrollToBottom={scrollToBottom} />
        </div>
        <div className="flex-none h-[120px]">
          <ChatControls
            submittedActions={submittedActions}
            onSubmit={onSubmit}
            scrollToBottom={scrollToBottom}
            inputChangeHandler={inputChangeHandler}
            inputActionTypeToggleHandler={inputActionTypeToggleHandler}
            inputActionType={inputActionType}
            chatInputText={chatInputText}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatDisplay;
