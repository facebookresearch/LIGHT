import React from "react";
import { Link, useHistory } from "react-router-dom";

import "../../styles.css";

import Unicorn from "../../assets/images/unicorn.jpg";

const AboutPage = (props) => {
  let history = useHistory();
  return (
    <div className="aboutpage-container">
      <div
        className="main-container"
        style={{
          backgroundColor: "#697b4d",
          alignItems: "center",
          height: "90%",
          padding: "3em",
        }}
      >
        <div style={{ width: "100%", flexDirection: "flexStart" }}>
          <div className="back-button" onClick={() => history.goBack()}>
            Back
          </div>
        </div>
        <h1 style={{ color: "white" }}>About LIGHT</h1>
        <p style={{ color: "white" }}>
          LIGHT is a research project focused on creating realistic interactive
          AI. LIGHT stands for
          <i>“Learning in Interactive Games with Humans and Text.”</i>
          The LIGHT game is a direct application of
          <a href="https://parl.ai/projects/light/"> our research</a>, and also
          acts as a live environment to allow players to interact with models
          and other players directly. We believe that by collecting gameplay
          interactions, we can train better agents to follow stories and create
          meaningful experiences for players.
        </p>
        <p style={{ color: "white" }}>
          We also feel that model-supported architectures can enable creators to
          tell their own stories. Thus, much of our project’s research will
          support user-created content in our world builder. By reducing the
          barrier of entry to create full, fleshed out worlds, it should be
          easier for anyone to create and share a slice of fantasy.
        </p>
        <p style={{ color: "white" }}>
          We plan to regularly release complete anonymized and sanitized data
          collected from within LIGHT, with the goal of enabling other
          researchers to extend upon our work, and this will be available for
          download from the project page. The complete source code for the
          project is available on our github.
        </p>
        <img style={{ width: "50%", height: "auto" }} src={Unicorn} />
      </div>
    </div>
  );
};

export default AboutPage;
