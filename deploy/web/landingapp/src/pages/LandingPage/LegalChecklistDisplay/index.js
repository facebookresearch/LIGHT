/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";
/* CUSTOM COMPONENTS */
import LegalCheck from "./LegalCheck";

const LegalChecklistDisplay = ({
  legalAgreements,
  loginStepIncreaseHandler,
}) => {
  /*--------------- LOCAL STATE ----------------*/
  const [legalInputResponses, setLegalInputResponses] = useState([]);
  const [formFullyCompleted, setFormFullyCompleted] = useState(false);
  /*--------------- UTIL ----------------*/
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

  useEffect(() => {
    console.log(
      "LEGAL AGREEMENTS :  ",
      legalAgreements,
      legalAgreements.length
    );
    let initialResponses = [];
    for (let i = 0; i < legalAgreements.length; i++) {
      console.log("for loop running :  ", i);
      initialResponses[i] = false;
    }
    console.log("INITIAL RESPONSES:  ", initialResponses);
    setLegalInputResponses(initialResponses);
  }, []);

  useEffect(() => {
    console.log("LEGAL INPUT RESPONSES:  ", legalInputResponses);
    let formComplete = completionChecker();
    setFormFullyCompleted(formComplete);
    // if (formComplete) {
    //   loginStepIncreaseHandler();
    // }
  }, [legalInputResponses]);
  /*--------------- HANDLERS ----------------*/
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
    <div className="w-3/4 text-3xl text-mono ">
      <h1 className="text-white text-4xl text-center underline">
        To get started, please acknowledge that you have read and agreed to
        every statement below by checking each box.
      </h1>
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
      {formFullyCompleted ? (
        <div className="w-full flex justify-center items-center">
          <button
            className="text-green-200 border-2 p-1 border-green-200 rounded"
            onClick={() => {
              loginStepIncreaseHandler();
            }}
          >
            SUBMIT AGREEMENT
          </button>
        </div>
      ) : null}
    </div>
  );
};

export default LegalChecklistDisplay;
