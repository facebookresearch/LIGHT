/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

import { Checkboxes } from './checkboxes.jsx';

function MaybeCheckboxChatMessage({ isSelf, duration, agentName, message = "", checkbox = null }) {
  const floatToSide = isSelf ? "right" : "left";
  const alertStyle = isSelf ? "alert-info" : "alert-warning";

  return (
    <div className="row" style={{ marginLeft: "0", marginRight: "0" }}>
      <div
        className={"alert message " + alertStyle}
        role="alert"
        style={{ float: floatToSide }}
      >
        <span style={{ fontSize: "16px", whiteSpace: "pre-wrap" }}>
          <b>{agentName}</b>: <span dangerouslySetInnerHTML={{ __html: message }}></span>
        </span>
        {checkbox}
      </div>
    </div>
  );
}

function RenderChatMessage({ message, mephistoContext, appContext, idx }) {
  // console.group("RenderChatMessage");
  console.groupCollapsed("RenderChatMessage");
  console.log(message);
  console.log(mephistoContext);
  console.log(appContext);
  console.log(idx);
  console.groupEnd();
  const { agentId, taskConfig } = mephistoContext;
  const { currentAgentNames } = appContext.taskContext;
  const { appSettings, setAppSettings } = appContext;
  const { checkboxValues, textFieldValues, messages } = appSettings;
  messages[idx] = [message['id'], message['text']]
  // const isHuman = (message.id === agentId || message.id == currentAgentNames[agentId]);
  // const isHuman = true;
  const isHuman = message.id === agentId || message.id === "Speaker 1";
  const annotationBuckets = taskConfig.annotation_buckets;
  const annotationIntro = taskConfig.annotation_question;

  var checkboxes = null;
  if (!isHuman && annotationBuckets !== null) {
    let thisBoxAnnotations = checkboxValues[idx];
    let thisBoxTextFields = textFieldValues[idx];
    if (!thisBoxAnnotations) {
      thisBoxAnnotations = Object.fromEntries(
        Object.keys(annotationBuckets.config).map(bucket => [bucket, false])
      )
      thisBoxTextFields = {'why_error':'', 'better_narration':''};
    }
    checkboxes = <div style={{"fontStyle": "italic"}}>
      <br />
      {annotationIntro}
      <br />
      <Checkboxes 
        annotations={thisBoxAnnotations} 
        textFields={thisBoxTextFields}
        onUpdateAnnotations={
          (newAnnotations) => {
            checkboxValues[idx] = newAnnotations;
            setAppSettings({checkboxValues});
          }
        }
        onUpdateTextFields={
          (newTexts) => {
            textFieldValues[idx] = newTexts;
            setAppSettings({textFieldValues});
          }
        }
        annotationBuckets={annotationBuckets} 
        turnIdx={idx} 
        // askReason={false} 
        askReason={true}
        // enabled={idx == appSettings.numMessages - 1}
        enabled={true}
      />
    </div>;
  }
  return (
    <MaybeCheckboxChatMessage
      isSelf={isHuman}
      agentName={isHuman ? "Some Hiking Party (you)" : "Game Engine"
        // message.id in currentAgentNames
        //   ? currentAgentNames[message.id]
        //   : message.id
      }
      message={message.text}
      taskData={message.task_data}
      messageId={message.message_id}
      checkbox={checkboxes}
    />
  );
}

export { RenderChatMessage, MaybeCheckboxChatMessage };