/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";
/* ICONS */
import { BsCheckLg } from "react-icons/bs";

const CheckBox = ({ checkFunction, checkStatus }) => {
  /*--------------- LOCAL STATE ----------------*/
  const [isChecked, setIsChecked] = useState(false);
  /*--------------- LIFECYLCLE ----------------*/
  useEffect(() => {
    let updatedIsChecked = checkStatus;
    setIsChecked(updatedIsChecked);
  }, [checkStatus]);
  /*--------------- HANDLERS ----------------*/
  const clickHandler = () => {
    checkFunction();
  };
  return (
    <div
      className="w-40 h-40 bg-blue-600 flex justify-center items-center"
      onClick={clickHandler}
    >
      {isChecked ? <BsCheckLg color="white" size={"9em"} /> : <div />}
    </div>
  );
};

export default CheckBox;
