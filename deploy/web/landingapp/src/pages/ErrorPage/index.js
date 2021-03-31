import React from "react";
import { Link } from "react-router-dom";

import "../../styles.css";

const ErrorPage = (props) => {
  return (
    <div className="errorpage-container">
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
        <h1 style={{ color: "white", textAlign: "center" }}>
          Oops, something went wrong.
        </h1>
      </div>
    </div>
  );
};

export default ErrorPage;
