import React from "react";
import { Link } from "react-router-dom";
import "../../styles.css";

const LogoutPage = (props) => {
  return (
    <div className="logoutpage-container">
      <div style={{ width: "100%", flexDirection: "flexStart" }}>
        <Link style={{ textDecoration: "none", color: "yellow" }} to="/">
          Back
        </Link>
      </div>
      <div>
        <h1 style={{ color: "white", marginLeft: "15px" }}>
          You are now logged out. Thank you for playing!
        </h1>
      </div>
    </div>
  );
};

export default LogoutPage;
