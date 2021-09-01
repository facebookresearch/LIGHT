import React from "react";
import { Link } from "react-router-dom";
import "./styles.css";

const LogoutPage = (props) => {
  return (
    <div className="logoutpage-container">
      <div className="logoutpage-body">
        <Link className="logoutpage-link" to="/">
          Back to Home
        </Link>
      </div>
      <div>
        <h1 className="logoutpage-text">
          You are now logged out. Thank you for playing!
        </h1>
      </div>
    </div>
  );
};

export default LogoutPage;
