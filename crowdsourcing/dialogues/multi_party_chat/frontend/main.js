/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */


import React from "react";
import ReactDOM from "react-dom";
import "bootstrap-chat/styles.css";

import { ChatApp, ChatMessage, DefaultTaskDescription } from "bootstrap-chat";

function RenderChatMessage({ message, mephistoContext, appContext, idx }) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;

  return (
    <div>
      <ChatMessage
        isSelf={message.id === agentId || message.id in currentAgentNames}
        agentName={
          message.id in currentAgentNames
            ? currentAgentNames[message.id]
            : message.id
        }
        message={message.text}
        taskData={message.task_data}
        messageId={message.message_id}
      />
    </div>
  );
}

function MainApp() {
  return (
    <ChatApp
      renderMessage={({ message, idx, mephistoContext, appContext }) => (
        <RenderChatMessage
          message={message}
          mephistoContext={mephistoContext}
          appContext={appContext}
          idx={idx}
          key={message.message_id + "-" + idx}
        />
      )}
      defaultAppSettings={{volume: 0}}
      renderSidePane={({ appContext, mephistoContext: { taskConfig } }) => (
        <DefaultTaskDescription
          chatTitle={taskConfig.chat_title}
          taskDescriptionHtml={taskConfig.task_description}
        >
          <b>You've been assigned: </b>
          {appContext.taskContext?.persona?.name}
          <p>
            <b>Your Persona: </b>
            {appContext.taskContext?.persona?.persona}
          </p>
          <b>You are in: </b>
          {appContext.taskContext?.location?.name}
          <p>
            {appContext.taskContext?.location?.description}
          </p>
        </DefaultTaskDescription>
      )}
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
