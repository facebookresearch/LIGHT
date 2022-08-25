/* REACT */
import React, { useEffect, useState, Fragment } from "react";
/* REDUX */
import { useAppDispatch, useAppSelector } from "../../../app/hooks";
/* ---- REDUCER ACTIONS ---- */
import { setReportModal } from "../../../features/modals/modals-slice";
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

  /*  LIFE CYLCE */

  /* HANDLERS */

  const closeReportModalHandler = () => {
    dispatch(setReportModal(false));
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
    scrollToBottom();
  };

  return (
    <Transition.Root show={showReportModal} as={Fragment}>
      <Dialog
        as="div"
        className="relative z-10"
        onClose={closeReportModalHandler}
      >
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        ></Transition.Child>

        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          enterTo="opacity-100 translate-y-0 sm:scale-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100 translate-y-0 sm:scale-100"
          leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
        >
          <Dialog.Panel className="relative bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-sm sm:w-full sm:p-6">
            <Dialog.Title
              as="h3"
              className="text-lg leading-6 font-medium text-gray-900"
            ></Dialog.Title>
          </Dialog.Panel>
        </Transition.Child>
      </Dialog>
      <div className="bg-white ">
        <div className="agent">
          <span>{reportModalActor}</span>
        </div>
        {reportModalMessage}
        <div>
          <b>Why are you reporting this message?</b>
        </div>
        <div>
          <label
            htmlFor="category"
            className="block text-sm font-medium text-gray-700"
          >
            Category
          </label>
          <select
            id="category"
            name="category"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-solid border-gray-300 border-4 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
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
            <label>Please describe issue here:</label>
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
    </Transition.Root>
  );
};
export default ReportMessageForm;
