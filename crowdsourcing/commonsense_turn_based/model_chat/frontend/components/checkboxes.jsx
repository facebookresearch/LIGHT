/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";

function Checkboxes({
  annotationBuckets,
  turnIdx,
  askReason,
  annotations,
  textFields,
  onUpdateAnnotations,
  onUpdateTextFields,
  enabled = true,
}) {
  var reasonComponent = (
    <div>
      <br></br>
      <div>
        {/* <div>Why did you select the checkboxes you did?</div> */}
        {/* <div>Please rewrite the narration without the errors you indicated:</div> */}
        <div>Describe in words what was wrong with the given narration:</div>
        <input 
          type="text" 
          id={'input_reason_' + turnIdx} 
          style={{ minWidth: '50%' }} 
          onChange={(evt) => {
            console.log(evt);
            let newVal = evt.target.value;
            let oldTextFields = Object.assign({}, textFields);
            oldTextFields['why_error'] = newVal;
            onUpdateTextFields(oldTextFields);
           }}
        />
      </div>
    </div>
  )
  "none_all_good"
  if (!askReason || annotations[''] || Object.keys(annotations).every(k => k === "none_all_good" || !annotations[k])) {
    // console.log(`askReason ${askReason}`)
    reasonComponent = '';
  }
  // TODO: add support for radio input type
  let input_type = "checkbox";
  const showLineBreaks = annotationBuckets.hasOwnProperty("show_line_breaks") ? annotationBuckets.show_line_breaks : false;
  const numBuckets = Object.keys(annotationBuckets.config).length;
  return (
    // <div key={'checkboxes_' + turnIdx}>
    <ul key={'checkboxes_' + turnIdx} style={{ listStyleType: "none" }}>
      {
        Object.keys(annotationBuckets.config).map((c, checkboxIdx) => (
          <div key={checkboxIdx}>
            {/* <span key={'span_' + c + '_' + turnIdx} key={checkboxIdx}> */}
            <li key={'span_' + c + '_' + turnIdx} key={checkboxIdx} style={{ listStyleType: "none" }}>
              <input
                type={input_type}
                id={c + '_' + turnIdx}
                name={'checkbox_group_' + turnIdx}
                onChange={(evt) => {
                  let newVal = evt.target.checked;
                  let oldAnnotations = Object.assign({}, annotations);
                  oldAnnotations[c] = newVal;
                  onUpdateAnnotations(oldAnnotations);
                }}
                disabled={!enabled}
              />
              <span style={{ marginRight: '15px' }}>
                {annotationBuckets.config[c].name}
              </span>
              {/* </span> */}
            </li>
            {(showLineBreaks && checkboxIdx < numBuckets - 1) ? <br></br> : ''}
          </div>
        ))
      }
      <div id={'checkbox_description_' + turnIdx} style={{ height: '24px' }}></div>
      {reasonComponent}
      <div>
        <br></br>
        <div>
          {/* <div>Why did you select the checkboxes you did?</div> */}
          {/* <div>Please rewrite the narration without the errors you indicated:</div> */}
          <div>Please write a better narration:</div>
          <input 
            type="text" 
            id={'input_rewrite_' + turnIdx} 
            style={{ minWidth: '50%' }} 
            onChange={(evt) => {
                console.log(evt);
                let newVal = evt.target.value;
                let oldTextFields = Object.assign({}, textFields);
                oldTextFields['better_narration'] = newVal;
                onUpdateTextFields(oldTextFields);
               }} />
        </div>
      </div>
      {/* </div> */}
    </ul>
  )
}
// showLineBreaks: show a line break after every checkbox other than the final one

export { Checkboxes };
