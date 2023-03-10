/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useEffect, useState, Fragment } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import {
  setReportModal,
  setReportModalSubmitted,
} from "../../../features/modals/modals-slice";
/* STYLES */
import { Dialog, Transition } from "@headlessui/react";

/* CONFIG */
import CONFIG from "../../../config.js";

import { Button } from "daisyui";
//
const ReportCategories = [
  "Report Inappropriate Content",
  "Report Bug",
  "Other",
];

//ReportMessageForm - Modal that allows users to specifically describe and report content for a variety of reasons.

const ReportMessageForm = () => {
  /* REDUX DISPATCH FUNCTION */
  const dispatch = useAppDispatch();
  /* ------ REDUX STATE ------ */
  //MODAL STATE
  const showReportModal = useAppSelector(
    (state) => state.modals.showReportModal
  );
  const reportModalMessageId = useAppSelector(
    (state) => state.modals.reportModalMessageId
  );
  const reportModalMessage = useAppSelector(
    (state) => state.modals.reportModalMessage
  );
  const reportModalActor = useAppSelector(
    (state) => state.modals.reportModalActor
  );
  /* LOCAL STATE */
  const [reportCategory, setReportCategory] = useState("");
  const [reportReason, setReportReason] = useState("");

  /* HANDLERS */

  const closeReportModalHandler = () => {
    dispatch(setReportModal(false));
  };

  const setReportModalHandler = (val) => {
    dispatch(setReportModal(val));
  };

  const categorySelectionHandler = (e) => {
    console.log("DROP DOWN TARGET:  ", e.target.value);
    setReportCategory(e.target.value);
  };

  const handleReportSubmission = () => {
    let base_url = window.location.protocol + "//" + CONFIG.hostname;
    if (CONFIG.port !== "80") {
      base_url += ":" + CONFIG.port;
    }
    console.log("REPORT PAYLOAD:  ", {
      eventId: reportModalMessageId,
      category: reportCategory,
      message: reportModalMessage,
      reason: reportReason,
    });

    window.parent.postMessage(
      JSON.stringify({
        caller: "report",
        category: reportCategory,
        message: reportModalMessage,
        reason: reportReason,
      }),
      "*"
    );

    fetch(`${base_url}/report`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
      body: JSON.stringify({
        category: reportCategory,
        message: reportModalMessage,
        reason: reportReason,
      }),
    });
    setReportReason("");
    setReportCategory("");
    dispatch(setReportModalSubmitted(true));
    dispatch(setReportModal(false));
  };

  return (
    <Transition.Root show={showReportModal} as={Fragment}>
      <Dialog
        as="div"
        className="_report-message-modal_ relative  z-10"
        onClose={setReportModalHandler}
      >
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-end sm:items-center justify-center min-h-full p-4 text-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative bg-base-100 rounded-lg p-10 text-left overflow-hidden shadow-2xl transform transition-all w-[50vw] min-w-fit">
                <Dialog.Title
                  as="h2"
                  className="text-xl leading-6 font-semibold text-base-content text-left mb-8"
                >
                  REPORT MESSAGE
                </Dialog.Title>
                <div className="text-md">
                  <div className="w-full flex flex-row mb-4">
                    <div className=" text-base-content w-[100px] flex-none opacity-70">
                      Character
                    </div>
                    <div className=" text-base-content font-medium">
                      {reportModalActor}
                    </div>
                  </div>
                  <div className="w-full flex flex-row mb-4">
                    <div className=" text-base-content w-[100px] flex-none opacity-70">
                      Message
                    </div>
                    <div className=" text-base-content font-medium max-w-lg">
                      {reportModalMessage}
                    </div>
                  </div>
                  <div className="w-full flex flex-row mb-4">
                    <label className=" text-base-content w-[100px] flex-none opacity-70 pt-2">
                      Reason
                    </label>
                    <div>
                      <select
                        id="category"
                        name="category"
                        className="p-2 rounded-md bg-base-200 focus:outline-primary active:outline-primary"
                        defaultValue=""
                        onChange={categorySelectionHandler}
                        value={reportCategory}
                      >
                        <option value={""} id={""}>
                          Select...
                        </option>
                        {ReportCategories.map((category, index) => (
                          <option key={category} id={index} value={category}>
                            {category}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  {reportCategory ? (
                    <>
                      <div className="w-full flex flex-row mb-6">
                        <label className="text-base-content w-[100px] flex-none opacity-70 pt-3">
                          Issue
                        </label>
                        <textarea
                          rows={3}
                          className="edit-message border-solid rounded-md p-3 w-full bg-base-200 focus:outline-primary active:outline-primary"
                          placeholder="Please describe the issue here"
                          value={reportReason}
                          onChange={(evt) => setReportReason(evt.target.value)}
                        />
                      </div>
                      <div className="text-right">
                        <button
                          type="submit"
                          className={`btn btn-ghost mr-2`}
                          onClick={closeReportModalHandler}
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          className={`btn btn-primary`}
                          disabled={reportReason.length === 0}
                          onClick={handleReportSubmission}
                        >
                          Report
                        </button>
                      </div>
                    </>
                  ) : null}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
};
export default ReportMessageForm;
