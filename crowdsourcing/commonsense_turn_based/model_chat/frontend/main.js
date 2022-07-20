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

import { CustomOnboardingChatApp } from "./components/chat_app_with_onboarding.jsx"
import { DefaultTaskDescription } from "bootstrap-chat";
import { ResponseComponent } from "./components/response_panes.jsx";
import { RenderChatMessage } from "./components/message.jsx";

// import "./override.css"
// import "/private/home/alexgurung/LIGHT/crowdsourcing/commonsense_turn_based/model_chat/override.css"

function MainApp() {
  const uniqueIDs = new Set();
  return (
    <CustomOnboardingChatApp
      propAppSettings={{ checkboxValues: {}, textFieldValues: {}, messages: {} }}
      renderMessage={({ message, idx, mephistoContext, appContext }) => {
        let { textFieldValues, messages } = appContext;
        if (textFieldValues === undefined) {
          appContext[textFieldValues] = {}
        }
        if (messages === undefined) {
          appContext[messages] = new Set();
        }
        let { text, update_id, id } = message;
        appContext[messages].add([idx, id, text]);
        let add_message = text !== undefined && !uniqueIDs.has(update_id);
        console.groupCollapsed(`CustomOnboardingChatApp: ${idx}`);
        console.log(`Adding message: ${add_message}`);
        console.log(`text: ${text !== undefined}`);
        console.log(`text: ${text}`);
        console.log(`unique has: ${!uniqueIDs.has(update_id)}`);
        console.log(`unique has: ${update_id} vs`);
        console.log(uniqueIDs);
        console.groupEnd();
        if (text !== undefined) {
          uniqueIDs.add(update_id);
        }
        return (
          <>
            {text !== undefined && idx <= 3 ? <RenderChatMessage
              message={message}
              mephistoContext={mephistoContext}
              appContext={appContext}
              idx={idx}
              key={message.message_id + "-" + idx}
            /> : null}
            {/* {text !== undefined ? <RenderChatMessage
          message={message}
          mephistoContext={mephistoContext}
          appContext={appContext}
          idx={idx}
          key={message.message_id + "-" + idx}
        /> : null} */}
            {/* <RenderChatMessage
          message={{id:"bot", text: "You got a fur"}}
          mephistoContext={mephistoContext}
          appContext={appContext}
          idx={idx}
          key={"some_id"}
        /> */}
          </>
        )
      }}
      renderSidePane={({ mephistoContext: { taskConfig, initialTaskData }, appContext: { taskContext } }) => {
        console.groupCollapsed("renderSidePane");
        console.log(initialTaskData);
        console.groupEnd();
        let { task_data } = initialTaskData;
        let gameText = undefined;
        let bold_current_player = undefined;
        if (task_data !== undefined) {
          // gameText = task_data.game_text_dropoutless;
          gameText = "<b>Context</b> <br>" + task_data.setting_context_text_dropoutless;
          gameText = gameText + "<br><br> <b>Previous Actions: </b> <br>" + task_data.action_context_text_dropoutless;
          bold_current_player = "<br><br><h3> You are: <b>" + task_data.current_player + "</b>. <br><br> Please give an <b>action</b> (not dialog) your character would want to perform and rate the response.</h3>";
          if (gameText !== undefined) {
            gameText = gameText.replaceAll("\n", "<br>");
            gameText = gameText + bold_current_player;
            // super hacky, easiest way to force left pane to be bigger
            gameText = gameText + `<style> .side-pane.col-xs-4 {width: 50%;} .chat-container-pane {height:100vh;}</style>`;
          }
        }
        return (
          <DefaultTaskDescription
            chatTitle={taskConfig.task_title}
            taskDescriptionHtml={
              gameText
              //   `You are in the Eating area of cave.<br>This room has rough, grey rock walls. The walls are lined with animal furs which are very fluffy and warm. The floor is dirt and gravel, which moves underfoot.
              // <br>
              // There\'s a dirt, a blanket, a gravel, a cave, a wall, a room, a bed, a fur, and a rock here.
              // <br>
              // Some bears and a fox are here.
              // <br>
              // You check yourself. You are some hiking party!
              // <br>
              // You are carrying a waterbottle and a compass, and wearing a short, a sunglasses, a watch, and a shoe.`

              // "HERE IS SOME TASK DESCRIPTION HTML, IT WOULD GO HERE"
              // taskConfig.left_pane_text.replace(
              //     "[persona_string_1]", taskContext.human_persona_string_1,
              // ).replace(
              //     "[persona_string_2]", taskContext.human_persona_string_2,
              // )
            }
          >
            {(taskContext.hasOwnProperty('image_src') && taskContext['image_src']) ? (
              <div>
                <h4>Conversation image:</h4>
                <span id="image">
                  <img src={taskContext.image_src} alt='Image' />
                </span>
                <br />
              </div>
            ) : null}
          </DefaultTaskDescription>
        )
      }}
      renderTextResponse={
        ({
          mephistoContext: { taskConfig, initialTaskData },
          mephistoContext: mephistoContext,
          appContext: { appSettings },
          onMessageSend,
          active,

        }) => {
          console.log(mephistoContext); 
          console.log(`active? ${active}`);
          return (
            <ResponseComponent
              mephistoContext={mephistoContext}
              appSettings={appSettings}
              taskConfig={taskConfig}
              active={active}
              onMessageSend={onMessageSend}
              initialTaskData={initialTaskData}
            />
          )
        }
      }
    />
  );
}

ReactDOM.render(<MainApp />, document.getElementById("app"));
