import React from "react";

import "../../styles.css";


const AboutPage = (props)=>{
    return(
    <div>
        <h1>About LIGHT</h1>
        <p>
            LIGHT is a research project focused on creating realistic interactive AI.
            LIGHT stands for
            <i>“Learning in Interactive Games with Humans and Text.”</i>
            The LIGHT game is a direct application of
            <a href="https://parl.ai/projects/light/">our research</a>, and also
            stands as a live environment to allow players to interact with models and
            other players directly. We believe that by collecting gameplay
            interactions, we can train better agents to follow stories and create
            meaningful experiences for players.
        </p>
        <p>
            We also feel that model-supported architectures can enable creators to
            tell their own stories. Thus, much of our project’s research supports
            supporting user-created content in our world builder. By reducing the
            barrier of entry to create full, fleshed out worlds, it should be easier
            for anyone to create and share a slice of fantasy.
        </p>
        <p>
            We plan to regularly release complete anonymized and sanitized data
            collected from within LIGHT, with the goal of enabling other researchers
            to extend upon our work, and this will be available for download from the
            project page. The complete source code for the project is available on our
            github.
        </p>
  </div>
    )
}

export default AboutPage