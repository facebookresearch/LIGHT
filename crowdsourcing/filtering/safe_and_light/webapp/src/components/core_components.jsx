/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

function OnboardingComponent({ onSubmit }) {
  return (
    <div>
      <Directions>
        This component only renders if you have chosen to assign an onboarding
        qualification for your task. Click the button to move on to the main
        task.
      </Directions>
      <button
        className="button is-link"
        onClick={() => onSubmit({ success: true })}
      >
        Move to main task.
      </button>
    </div>
  );
}

function LoadingScreen() {
  return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
  return (
    <section class="hero is-light">
      <div class="hero-body">
        <div class="container">
          <p class="subtitle is-5">{children}</p>
        </div>
      </div>
    </section>
  );
}


function TextAnnotator({ text, idx, safety, fantasy, updateSafety, updateFantasy }) {
  return (
    <div className="container">
      <p className="subtitle is-5"></p>
      <p className="title is-3 is-spaced">{text}</p>
      <div className="field is-grouped">
        <div className="control">
          <span key={'span_safety_safe_' + idx}>
            <input
              type={'checkbox'}
              id={'cbs-s-' + idx}
              name={'safety-' + idx}
              onChange={(evt) => {
                updateSafety(true);
              }}
              checked={safety === true}
            />
            SAFE&nbsp;&nbsp;
          </span>
          <span key={'span_safety_unsafe_' + idx}>
            <input
              type={'checkbox'}
              id={'cbs-f-' + idx}
              name={'safety-' + idx}
              onChange={(evt) => {
                updateSafety(false);
              }}
              checked={safety === false}
            />
            likely UNSAFE&nbsp;&nbsp;
          </span>
        </div>
        <div className="control">
          <span key={'span_fantasy_safe_' + idx}>
            <input
              type={'checkbox'}
              id={'cbs-s-' + idx}
              name={'fantasy-' + idx}
              onChange={(evt) => {
                updateFantasy(true);
              }}
              checked={fantasy === true}
            />
            can be FANTASY&nbsp;&nbsp;
          </span>
          <span key={'span_fantasy_unsafe_' + idx}>
            <input
              type={'checkbox'}
              id={'cbs-f-' + idx}
              name={'fantasy-' + idx}
              onChange={(evt) => {
                updateFantasy(false);
              }}
              checked={fantasy === false}
            />
            only REAL-world&nbsp;&nbsp;
          </span>
        </div>
        <br />
        <br />
        <br />
      </div>
    </div>
  );
}


function SimpleFrontend({ taskData, isOnboarding, onSubmit }) {
  const [ratings, setRatings] = React.useState([
    [null, null],
    [null, null],
    [null, null],
    [null, null],
    [null, null],
    [null, null],
    [null, null],
    [null, null],
    [null, null],
    [null, null],
  ])

  let canSubmit = true;
  for (let idx in ratings) {
    let curr = ratings[idx];
    if (curr[0] === null || curr[1] === null) {
      canSubmit = false;
      break;
    }
  }

  if (!taskData) {
    return <LoadingScreen />;
  }
  if (isOnboarding) {
    return <OnboardingComponent onSubmit={onSubmit} />;
  }
  let annotators = taskData.text_lines.map(
    (v, idx) => <TextAnnotator
      text={v}
      idx={idx}
      safety={ratings[idx][0]}
      fantasy={ratings[idx][1]}
      updateSafety={(val) => {
        let new_ratings = [...ratings];
        new_ratings[idx][0] = val;
        setRatings(new_ratings);
      }}
      updateFantasy={(val) => {
        let new_ratings = [...ratings];
        new_ratings[idx][1] = val;
        setRatings(new_ratings);
      }}
    />
  )
  return (
    <div>
      <Directions>
        Directions -- Please rate the below sentences as being SAFE or UNSAFE to say, and 
        as being relevant to say in a medieval FANTASY setting, or only in a REAL setting.
        More detail about this repeated below:
        <DescInstructions />
      </Directions>
      <section class="section">
        {annotators}
      </section>
      <section class="section">
        <button
          className="button is-success is-large"
          onClick={() => onSubmit({ ratings: ratings })}
          disabled={!canSubmit}
        >
          Submit
        </button>
      </section>
    </div>
  );
}


function DescInstructions() {
  return (
    <div>
      <b>Safety:</b> Each sentence should be marked as either SAFE or UNSAFE. <br/> Things that are SAFE 
      should be anything you can imagine would be safe to say in a fantasy text adventure setting 
      (where minor combat and violence is possible). 
      <br/>
      Things that are UNSAFE include anything that:
      <ul>
        <li>&nbsp;&nbsp;-&nbsp;Is sexually explicit or highly suggestive in nature. </li>
        <li>&nbsp;&nbsp;-&nbsp;Is sexist, racist, or otherwise directly offensive or hateful to a real-world group of people. </li>
        <li>&nbsp;&nbsp;-&nbsp;Encourages self-harm.</li>
        <li>&nbsp;&nbsp;-&nbsp;Encourages use of real-world illicit drugs.</li>
        <li>&nbsp;&nbsp;-&nbsp;Includes descriptions of particularly graphic violence.</li>
        <li>&nbsp;&nbsp;-&nbsp;Is directly offensive to a religion. </li>
      </ul>
      <br/>
      <b>Medieval Fantasy:</b> Each sentence should be marked as either FANTASY or REAL. <br/> Things that are FANTASY 
      should be anything that <b>could reasonably said</b> by a character in a medieval setting, one without 
      awareness of modern-day technologies, popular culture, or recent events. 
      <br/>
      Things that are REAL include anything that:
      <ul>
        <li>&nbsp;&nbsp;-&nbsp;Directly references a real-world person or location. </li>
        <li>&nbsp;&nbsp;-&nbsp;Directly references a modern-day event. </li>
        <li>&nbsp;&nbsp;-&nbsp;Uses real-world popular culture references. </li>
        <li>&nbsp;&nbsp;-&nbsp;Talks about modern-day technologies (anything after the era of horse-and-carraidge). </li>
        <li>&nbsp;&nbsp;-&nbsp;Would be out-of-character for a medieval fantasy character to say. </li>
      </ul>
    </div>
  );
}

export { LoadingScreen, DescInstructions, SimpleFrontend as BaseFrontend };
