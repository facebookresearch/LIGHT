import React from "react";
import { Link } from "react-router-dom";

import "../../styles.css";

const TermsPage = (props) => {
  return (
    <div className="termspage-container">
      <div
        className="main-container"
        style={{
          backgroundColor: "#253a20",
          alignItems: "center",
          height: "90%",
          padding: "3em",
          color: "white",
          opacity: "0.7",
          justifyContent: "flex-start",
        }}
      >
        <div style={{ width: "100%", flexDirection: "flexStart" }}>
          <Link style={{ textDecoration: "none", color: "yellow" }} to="/">
            Back
          </Link>
        </div>
        <h1 style={{ color: "white" }}>Terms</h1>
        <p>
          Facebook will process the messages you send in playing the game in
          accordance with our Data Policy (<a href="http://facebook.com/policy" target="_blank">facebook.com/policy</a>). Messages you
          send in playing the game may be used by Facebook for research purposes
          and as otherwise specified in our Data Policy, and may be used by
          and/or shared with third parties in connection with this research.
        </p>
        <p>
          This may involve public disclosure of the messages as part of a
          research paper or data set. We will take measures to remove any
          information that directly identifies you before doing so, but cannot
          guarantee that messages will be completely anonymous. Do not send
          personal information (for example, name, address, email, or phone
          number) in your messages.
        </p>
        <p>
          Facebook's Community Standards apply and you may not use any racist,
          sexist, or otherwise offensive language, or harass other players. If
          you violate our policies you may be reported and blocked.
        </p>
      </div>
    </div>
  );
};

export default TermsPage;
