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
      className="w-20 h-20 bg-blue-600 flex justify-center items-center rounded-2xl mr-2"
      onClick={clickHandler}
    >
      <div className="w-20 h-20 flex justify-center items-center ">
        {isChecked ? <BsCheckLg color="white" size={60} /> : <div />}
      </div>
    </div>
  );
};

export default CheckBox;
