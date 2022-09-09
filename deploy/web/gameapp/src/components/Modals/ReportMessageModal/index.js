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

const ReportCategories = [
  "Report Inappropriate Content",
  "Report Bug",
  "Other",
];

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

  /*  LIFE CYCLE */

  /* HANDLERS */

  const closeReportModalHandler = () => {
    dispatch(setReportModal(false));
  };

  const openReportModalHandler = () => {
    dispatch(setReportModal(open));
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

    window.top.postMessage(
      JSON.stringify({
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
        className="relative z-10"
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
              <Dialog.Panel className="relative bg-gray-700 rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-sm sm:w-full sm:p-6">
                <Dialog.Title
                  as="h3"
                  className="text-lg leading-6 font-medium underline text-white text-center"
                >
                  REPORT MESSAGE
                </Dialog.Title>
                <div className=" ">
                  <div className="w-full flex flex-row justify-start items-center p-2">
                    <span className=" text-white border rounded p-1 mr-1 border-green-400 bg-green-400">
                      CHARACTER:{" "}
                    </span>
                    <span className=" text-white">{reportModalActor}</span>
                  </div>
                  <div className="w-full flex flex-row justify-start  p-2">
                    <span className=" text-white border rounded p-1 mr-1 border-green-400 bg-green-400">
                      MESSAGE:{" "}
                    </span>
                    <span className=" text-white">{reportModalMessage}</span>
                  </div>
                  <div>
                    <b className=" text-white ">
                      Why are you reporting this message?
                    </b>
                  </div>
                  <div>
                    <label
                      htmlFor="category"
                      className="block text-sm font-medium text-white underline text-center"
                    >
                      Category
                    </label>
                    <select
                      id="category"
                      name="category"
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-solid border-green-400 border-4 focus:outline-none focus:ring-green-400 focus:border-green-400 sm:text-sm rounded-md"
                      defaultValue=""
                      onChange={categorySelectionHandler}
                      value={reportCategory}
                    >
                      <option value={""} id={""}></option>
                      {ReportCategories.map((category, index) => (
                        <option key={category} id={index} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>
                  </div>
                  {reportCategory ? (
                    <>
                      <label className="text-white">
                        Please describe issue here:
                      </label>
                      <input
                        className="edit-message border-solid border-gray-300 border-4"
                        defaultValue={"Enter reason here"}
                        value={reportReason}
                        onChange={(evt) => setReportReason(evt.target.value)}
                      />
                      <button
                        type="submit"
                        className={` w-20 items-start px-1.5 py-0.5 border border-transparent text-lg font-medium rounded shadow-sm text-white bg-red-600`}
                        disabled={reportReason.length === 0}
                        onClick={handleReportSubmission}
                      >
                        Report
                      </button>
                      <button
                        type="submit"
                        className={` w-20 items-start px-1.5 py-0.5 border border-transparent text-lg font-medium rounded shadow-sm text-white bg-gray-600`}
                        onClick={closeReportModalHandler}
                      >
                        Cancel
                      </button>
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
