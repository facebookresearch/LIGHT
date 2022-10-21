/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";

const TypewriterText = ({ text, welcomeStepAdvancementHandler }) => {
  const [remainingTextToType, setRemainingTextToType] = useState(text);
  const [typedText, setTypedText] = useState("");

  /*--------------- LIFECYLCLE ----------------*/
  useEffect(() => {
    setRemainingTextToType(text);
  }, []);
  useEffect(() => {
    const timeout = setTimeout(() => {
      setTypedText(text.slice(0, typedText.length + 1));
    }, 100);
    if (text.length === typedText.length) {
      welcomeStepAdvancementHandler();
    }
    return () => clearTimeout(timeout);
  }, [typedText]);
  /*--------------- HANDLERS ----------------*/

  return (
    <div className=" text-white">
      <p>{typedText}</p>
    </div>
  );
};

export default TypewriterText;
