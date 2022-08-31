/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* STYLES */
import "./styles.css";
/* IMAGES */
import Scribe from "../../../assets/images/scribe.png";

const TutorialContent = ({ tip }) => {
  const [tipPage, setTipPage] = useState(0);
  const { title, description } = tip;
  return (
    <div className="tip-container">
      <div className="tip-portrait__container">
        <img className="tip-portrait" src={Scribe} />
      </div>
      <div className="tip-chatbubble">
        <h5 className="tip-chatbubble__header">{title}</h5>
        <p className="tip-chatbubble__body">{description}</p>
      </div>
    </div>
  );
};

export default TutorialContent;
