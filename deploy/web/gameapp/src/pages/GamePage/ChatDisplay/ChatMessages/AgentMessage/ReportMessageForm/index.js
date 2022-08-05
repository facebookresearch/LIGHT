/* REACT */
import React, { useState } from "react";
/* STYLES */

/* ICONS */
import { FaStar } from "react-icons/fa";

/* CONFIG */
import CONFIG from "../../../../../../config.js";

const ReportCategories = [
  "Report Inappropriate Content",
  "Report Bug",
  "Other",
];

const ReportMessageForm = ({
  eventId,
  reportedMessage,
  caller,
  actor,
  exitReportMode,
}) => {
  let classNames = "message type-dialogue ";
  if (["tell", "say", "whisper"].includes(caller)) {
    reportedMessage = "&ldquo;" + reportedMessage + "&rdquo;";
    classNames = "message type-dialogue ";
  }
  classNames += "other";
  const [reportCategory, setReportCategory] = useState("");
  const [reportReason, setReportReason] = useState("");
  const [isReported, setReported] = useState(false);

  /* HANDLERS */
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
      eventId: eventId,
      category: reportCategory,
      message: reportedMessage,
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
        message: reportedMessage,
        reason: reportReason,
      }),
    });
    setReportReason("");
    setReported(true);
    exitReportMode();
  };

  return (
    <div className={classNames}>
      <div className="agent">
        <span>{actor}</span>
      </div>
      {reportedMessage}
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
            onClick={exitReportMode}
          >
            Cancel
          </button>
        </>
      ) : null}
    </div>
  );
};
export default ReportMessageForm;
