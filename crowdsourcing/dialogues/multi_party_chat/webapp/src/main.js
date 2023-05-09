/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import ReactDOM from "react-dom";
import "bootstrap-chat/styles.css";
import TextTransition, { presets } from "react-text-transition";
import { Button } from "react-bootstrap";
import { ChatApp, DefaultTaskDescription, INPUT_MODE, TextResponse, FormResponse, DoneResponse } from "bootstrap-chat";
import valid_utterance from "./utils";

function ChatMessage({ isSelf, idx, agentName, color, message = "" }) {
  const floatToSide = isSelf ? "right" : "left";
  const alertStyle = isSelf ? "alert-info" : color;

  return (
    <div className="row" style={{ marginLeft: "0", marginRight: "0" }}>
      <div
        className={"alert message " + alertStyle}
        role="alert"
        style={{ float: floatToSide }}
      >
        <span style={{ fontSize: "16px", whiteSpace: "pre-wrap" }}>
          <b>{agentName}</b>: {message}
        </span>
      </div>
    </div>
  );
}

function RenderChatMessage({ message, mephistoContext, appContext, idx }) {
  const { agentId } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;

  const partners = appContext.taskContext?.partners ?? []
  const colors = ['alert-success', 'alert-warning']
  const colorMap = Object.fromEntries(partners.map((partner, index) => [partner.name, colors[index]]));
  colorMap['Coordinator'] = 'alert-danger';

  return (
    <div>
      <ChatMessage
        isSelf={message.id === agentId || message.id in currentAgentNames}
        agentName={
          message.id in currentAgentNames
            ? currentAgentNames[message.id]
            : message.id
        }
        color={colorMap[message.id]}
        message={message.text}
        taskData={message.task_data}
        messageId={message.message_id}
      />
    </div>
  );
}

function MainApp() {
  const [showForm, setShowForm] = React.useState(false);
  const toggleShowForm = () => {
    setShowForm(!showForm)
  }

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
      renderResponse={({ onMessageSend, inputMode, appContext }) => {

        const checkMessageAndSend = async (message) => {
          const { text } = message;
          if (valid_utterance(text)) {
            await onMessageSend(message)
          }
        }

        if (appContext.taskContext?.has_submitted) {
          return (
            <div className="response-bar">
              <h3>Thanks for submitting! You can now close the task.</h3>
            </div>
          )
        }
        return inputMode === INPUT_MODE.INACTIVE ? (
          <DoneResponse
            onTaskComplete={appContext.onTaskComplete}
            onMessageSend={onMessageSend}
            doneText={appContext.taskContext?.doneText}
            isTaskDone={appContext.taskContext?.task_done}
          />
        )
          : (
            <>
              <TextResponse
                onMessageSend={checkMessageAndSend}
                active={inputMode !== INPUT_MODE.WAITING}
              />

              {appContext.taskContext?.task_done && (
                <div className="response-type-module">
                  <div className="response-bar">
                    <h3>Thanks for completing the task!</h3>
                  </div>
                  <div>You can keep going or submit and leave anytime.</div>
                </div>
              )}
              {appContext.taskContext?.["respond_with_form"] && (
                <Button onClick={toggleShowForm} className="btn btn-success">
                  {showForm ? 'Hide' : 'Finish'}
                </Button>
              )}
              {appContext.taskContext?.["respond_with_form"] && showForm && (
                <FormResponse
                  onMessageSend={(data) => appContext.onTaskComplete(data)}
                  active
                  formOptions={appContext.taskContext?.["respond_with_form"]}
                />
              )}
            </>
          )
      }}
      defaultAppSettings={{ volume: 0 }}
      renderSidePane={({ appContext, mephistoContext: { taskConfig } }) => (
        <DefaultTaskDescription
          chatTitle={taskConfig.chat_title}
          taskDescriptionHtml={taskConfig.task_description}
        >
          <h3>
            You've been assigned: &nbsp;
            <TextTransition
              inline
              text={appContext.taskContext?.persona?.name ?? ''}
              springConfig={presets.wobbly}
              style={{ color: 'red' }}
            />
          </h3>
          <p>
            {appContext.taskContext?.persona?.persona}
          </p>
          <h3>
            You are in: &nbsp;
            <TextTransition
              inline
              text={appContext.taskContext?.location?.name ?? ''}
              springConfig={presets.wobbly}
              style={{ color: 'red' }}
            />
          </h3>
          <p>
            {appContext.taskContext?.location?.description}
          </p>
          <h3>Your Partners:</h3>
          <ul>
            {appContext.taskContext?.partners?.map(partner => (
              <li style={{ fontSize: 20, fontWeight: 'semibold' }}>
                <TextTransition
                  text={partner.name ?? ''}
                  springConfig={presets.wobbly}
                  style={{ color: 'red' }}
                />
              </li>
            ))}
          </ul>
          <h3>
            You have spoken: {appContext.taskContext?.current_dialogue_turn ?? '0'} turn(s)
          </h3>
          <p>
            Task can be completed when everyone has spoken at least <b>8</b> turns
          </p>
        </DefaultTaskDescription>
      )}
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));