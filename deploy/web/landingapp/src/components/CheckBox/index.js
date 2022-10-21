/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";
/* ICONS */
import { BsCheckLg } from "react-icons/bs";

const CheckBox = ({ checkFunction }) => {
  /*--------------- LOCAL STATE ----------------*/
  const [isChecked, setIsChecked] = useState(false);
  /*--------------- LIFECYLCLE ----------------*/

  /*--------------- HANDLERS ----------------*/
  const clickHandler = () => {
    checkFunction();
    let updatedIsChecked = !isChecked;
    setIsChecked(updatedIsChecked);
  };
  return (
    <div
      className={` ${
        isCurrentStep ? "text-green-200 hover:text-green-50" : "text-green-800"
      }`}
      onClick={clickHandler}
    >
      {isChecked ? <BsCheckLg /> : null}
    </div>
  );
};

export default CheckBox;
