/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Link, useHistory } from "react-router-dom";

import "./styles.css";

import Unicorn from "../../assets/images/unicorn.jpg";

const AboutPage = (props) => {
  let history = useHistory();
  return (
    <div className="aboutpage-container">
      <div className="aboutpage-body">
        <div style={{ width: "100%", flexDirection: "flexStart" }}>
          <div className="back-button" onClick={() => history.goBack()}>
            Back
          </div>
        </div>
        <h1 className="aboutpage-header">About LIGHT</h1>
        <div className="aboutpage-text__container">
          <p>
            LIGHT is a research project focused on creating realistic
            interactive AI. LIGHT stands for
            <i>“Learning in Interactive Games with Humans and Text.”</i>
            The LIGHT game is a direct application of
            <a
              style={{ color: "yellow", fontWeight: "bold" }}
              href="https://parl.ai/projects/light/"
            >
              {" "}
              our research
            </a>
            , and also acts as a live environment to allow players to interact
            with models and other players directly. We believe that by
            collecting gameplay interactions, we can train better agents to
            follow stories and create meaningful experiences for players.
          </p>
          <p>
            We also feel that model-supported architectures can enable creators
            to tell their own stories. Thus, much of our project’s research will
            support user-created content in our world builder. By reducing the
            barrier of entry to create full, fleshed out worlds, it should be
            easier for anyone to create and share a slice of fantasy.
          </p>
          <p>
            We plan to regularly release complete anonymized and sanitized data
            collected from within LIGHT, with the goal of enabling other
            researchers to extend upon our work, and this will be available for
            download from the project page. The complete source code for the
            project is available on our github.
          </p>
        </div>
        <img className="aboutpage-image" src={Unicorn} />
      </div>
    </div>
  );
};

export default AboutPage;
