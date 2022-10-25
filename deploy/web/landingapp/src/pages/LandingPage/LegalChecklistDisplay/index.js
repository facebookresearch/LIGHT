/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";
/* CUSTOM COMPONENTS */
import LegalCheck from "./LegalCheck";

//LegalChecklistDisplay - This Component renders checkbox forms to confirm users approve of the condition required to proceed to the intro or the game.
const LegalChecklistDisplay = ({
  legalAgreements,
  postLoginStepIncreaseHandler,
}) => {
  /*--------------- LOCAL STATE ----------------*/
  const [legalInputResponses, setLegalInputResponses] = useState([]); //Tracks Users answers
  const [formFullyCompleted, setFormFullyCompleted] = useState(false); //Tracks when all conditions have been accepted
  /*--------------- UTIL ----------------*/
  //completionChecker - iterates through responses and sets formFullyCompleted state to true when all condition have been accepted
  const completionChecker = () => {
    let formComplete = false;
    if (legalInputResponses.length) {
      for (let i = 0; i < legalInputResponses.length; i++) {
        let currentResponse = legalInputResponses[i];
        if (currentResponse === false) {
          return (formComplete = false);
        } else {
          formComplete = true;
        }
      }
    }
    return formComplete;
  };

  /*--------------- LIFECYLCLE ----------------*/
  //Sets initial responses to an array of false values
  useEffect(() => {
    let initialResponses = [];
    for (let i = 0; i < legalAgreements.length; i++) {
      initialResponses[i] = false;
    }
    setLegalInputResponses(initialResponses);
  }, []);

  //Checks if the form is completed after each response change
  useEffect(() => {
    let formComplete = completionChecker();
    setFormFullyCompleted(formComplete);
  }, [legalInputResponses]);
  /*--------------- HANDLERS ----------------*/
  //legalCheckListResponseHandler - togglese value of the responsee of the associated condition
  const legalCheckListResponseHandler = (termIndex) => {
    let updatedResponses = legalInputResponses.map((response, index) => {
      if (index === termIndex) {
        let updatedResponse = !response;
        return updatedResponse;
      } else {
        return response;
      }
    });
    setLegalInputResponses(updatedResponses);
  };

  return (
    <div className="w-3/4 text-2xl text-mono ">
      <h2 className="text-white text-3xl text-center">
        To get started, please acknowledge that you have read and agreed to
        every statement below by checking each box.
      </h2>
      <div className="flex flex-col justify-start items-start">
        {legalAgreements.map((legalItem, index) => {
          let responseHandler = () => legalCheckListResponseHandler(index);
          return (
            <LegalCheck
              key={legalItem}
              responses={legalInputResponses}
              itemIndex={index}
              legalItem={legalItem}
              responseHandler={responseHandler}
            />
          );
        })}
      </div>
      <div className="w-full flex justify-center items-center">
        <button
          disabled={!formFullyCompleted}
          className={` ${
            formFullyCompleted
              ? "text-green-200 border-green-200 hover:text-blue-400 hover:border-blue-400"
              : "text-gray-200 border-gray-200"
          } border-2 p-1 rounded`}
          onClick={() => {
            postLoginStepIncreaseHandler();
          }}
        >
          Accept Agreement
        </button>
      </div>
    </div>
  );
};

export default LegalChecklistDisplay;
