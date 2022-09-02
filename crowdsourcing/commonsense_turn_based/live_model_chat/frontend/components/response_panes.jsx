/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

import { Button, Col, ControlLabel, Form, FormControl, FormGroup } from "react-bootstrap";


function hasAnyAnnotations(annotations) {
  if (!annotations) {
    return false;
  }
  for (const key in annotations) {
    if (annotations[key] === true) {
      return true;
    }
  }
  return false;
}

function RatingSelector({ active, ratings, sending, ratingQuestion, ratingIndex, setRatings }) {
  const ratingOptions = [<option key="empty_option" />].concat(
    ["1", "2", "3", "4", "5"].map((option_label, index) => {
      return (
        <option key={"option_" + index.toString()}>{option_label}</option>
      );
    })
  );

  function handleRatingSelection(val) {
    const newRatings = ratings.map((item, index) => {
      if (index === ratingIndex) {
        return val;
      } else {
        return item;
      }
    });
    setRatings(newRatings);
  }

  return (
    <FormGroup key={"final_survey_" + ratingIndex.toString()}>
      <Col
        componentClass={ControlLabel}
        sm={6}
        style={{ fontSize: "14px" }}
      >
        {ratingQuestion}
      </Col>
      <Col sm={5}>
        <FormControl
          componentClass="select"
          style={{ fontSize: "14px" }}
          value={ratings[ratingIndex]}
          onChange={(e) => handleRatingSelection(e.target.value)}
          disabled={!active || sending}
        >
          {ratingOptions}
        </FormControl>
      </Col>
    </FormGroup>
  );
}

function FinalSurvey({ taskConfig, onMessageSend, active, currentCheckboxes, currentRatingValues, handleSubmit }) {
  const [sending, setSending] = React.useState(false);

  // Set up multiple response questions
  // let ratingQuestions = taskConfig.final_rating_question.split("|");
  let ratingQuestions = taskConfig.final_rating_question.split("|").filter(q => q !== "");
  let initialRatings = [];
  for (let _ of ratingQuestions) {
    initialRatings.push("");
  }
  const [ratings, setRatings] = React.useState(initialRatings)

  const tryMessageSend = React.useCallback(() => {
    let all_ratings_filled = ratings.every((r) => r !== "");
    let rating = ratings.join('|');
    let finished = false;
    let tFv = currentRatingValues.textFieldValues;
    if (tFv[3] !== undefined) {
      if (tFv[3]['better_narration'].length > 0) {
        finished = true;
      }
    }
    if (!finished) {
      alert('Please provide a better narration');
      return;
    }
    
    // if (all_ratings_filled && active && !sending) {
    if (!sending) {
      setSending(true);
      onMessageSend({
        text: "",
        task_data: {
          problem_data_for_prior_message: currentCheckboxes,
          final_rating: rating,
          all_ratings: currentRatingValues,
        },
      }).then(() => {
        handleSubmit({
          problem_data_for_prior_message: currentCheckboxes,
          final_rating: rating,
          all_ratings: currentRatingValues,

        }).then(() => {
          setSending(false);
        });
      });
    }
  }, [active, sending, ratings, onMessageSend]);

  const listRatingSelectors = ratingQuestions.map((ratingQuestion, ratingIndex) => {
    return (
      <RatingSelector
        active={active}
        ratings={ratings}
        sending={sending}
        ratingQuestion={ratingQuestion}
        ratingIndex={ratingIndex}
        setRatings={setRatings}
        key={ratingIndex}
      >
      </RatingSelector>
    );
  });

  if (listRatingSelectors.length > 1) {
    // Show ratings to the right of the questions
    return (
      <div className="response-type-module">
        <div>
          You've completed the conversation. Please annotate the final turn, fill out
          the following, and hit Done.
        </div>
        <br />
        <Form
          horizontal
        >
          {listRatingSelectors}
          <Button
            className="btn btn-submit submit-response"
            id="id_send_msg_button"
            disabled={!active || sending}
            onClick={() => tryMessageSend()}
          >
            Done
          </Button>
        </Form>
      </div>
    );
  } else {
    // Show the single rating below the single question
    return (
      <div className="response-type-module">
        <div>
          You've completed the conversation. Please annotate the final turn and hit Done.
        </div>
        <br />
        <div className="response-bar">
          {listRatingSelectors}
          <Button
            className="btn btn-submit submit-response"
            id="id_send_msg_button"
            disabled={!active || sending}
            onClick={() => tryMessageSend()}
          >
            Done
          </Button>
        </div>
      </div>
    );
  }
}

function CheckboxTextResponse({ onMessageSend, active, currentCheckboxes, currentRatingValues, textContext, currentPlayer }) {
  const [textValue, setTextValue] = React.useState("");
  const [sending, setSending] = React.useState(false);

  const inputRef = React.useRef();

  React.useEffect(() => {
    if (active && inputRef.current && inputRef.current.focus) {
      inputRef.current.focus();
    }
  }, [active]);

  const tryMessageSend = React.useCallback(() => {
    if (textValue !== "" && active && !sending) {
      setSending(true);
      onMessageSend({
        text: textValue,
        task_data: { problem_data_for_prior_message: currentCheckboxes, all_ratings: currentRatingValues, textContext, currentPlayer }
      }).then(() => {
        setTextValue("");
        setSending(false);
      });
    }
  }, [textValue, active, sending, onMessageSend]);

  const handleKeyPress = React.useCallback(
    (e) => {
      if (e.key === "Enter") {
        tryMessageSend();
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
      }
    },
    [tryMessageSend]
  );

  return (
    <div className="response-type-module">
      <div className="response-bar">
        <FormControl
          type="text"
          className="response-text-input"
          inputRef={(ref) => {
            inputRef.current = ref;
          }}
          value={textValue}
          placeholder="Please enter action here..."
          onKeyPress={(e) => handleKeyPress(e)}
          onChange={(e) => setTextValue(e.target.value)}
          disabled={!active || sending}
        />
        <Button
          className="btn btn-primary submit-response"
          id="id_send_msg_button"
          disabled={textValue === "" || !active || sending}
          onClick={() => tryMessageSend()}
        >
          Do Action
          <br></br>
          (No Dialog)
        </Button>
      </div>
    </div>
  );
}

function ResponseComponent({ taskConfig, initialTaskData, appSettings, onMessageSend, active, mephistoContext }) {
  // function ResponseComponent({ mephistoContext, appSettings, onMessageSend, active }) {
  // let {taskConfig} = mephistoContext;
  // console.log("MEPHISTO CONTEXT");
  // console.log(mephistoContext);
  const { handleSubmit } = mephistoContext;
  const lastMessageIdx = appSettings.numMessages - 1;
  const lastMessageAnnotations = appSettings.checkboxValues[lastMessageIdx];
  const { checkboxValues, textFieldValues, messages } = appSettings;
  const currentRatingValues = { checkboxValues, textFieldValues, messages };
  const { task_data } = initialTaskData;
  let textContext = undefined;
  let currentPlayer = undefined;
  if (task_data !== undefined) {
    textContext = task_data.game_text_dropoutless;
    currentPlayer = task_data.current_player;
  }

  // console.log(`taskConfig.annotation_buckets === null; ${taskConfig.annotation_buckets === null}`)
  // console.log(`hasAnyAnnotations(lastMessageAnnotations); ${hasAnyAnnotations(lastMessageAnnotations)}`)

  // const computedActive = (
  //   taskConfig.annotation_buckets === null ||
  //   hasAnyAnnotations(lastMessageAnnotations) & active
  // );
  const computedActive = true;

  if (lastMessageIdx >= taskConfig.min_num_turns * 2) {
    return (
      <FinalSurvey
        onMessageSend={onMessageSend}
        taskConfig={taskConfig}
        active={computedActive}
        currentCheckboxes={lastMessageAnnotations}
        currentRatingValues={currentRatingValues}
        handleSubmit={handleSubmit}
      />
    );
  } else {
    return (
      <CheckboxTextResponse
        onMessageSend={onMessageSend}
        active={computedActive}
        currentCheckboxes={lastMessageAnnotations}
        currentRatingValues={currentRatingValues}
        textContext={textContext}
        currentPlayer={currentPlayer}
      />
    );
  }
}

export { ResponseComponent };