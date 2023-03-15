/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* REACT */
import React, { useState, useEffect } from "react";
/* ICONS */
import { BsCheckLg } from "react-icons/bs";

//CheckBox - Custom Checkbox component designed to be larger than daisyUI Checkboxes
const CheckBox = ({ checkFunction, checkStatus }) => {
  /*--------------- LOCAL STATE ----------------*/
  const [isChecked, setIsChecked] = useState(false);
  /*--------------- LIFECYLCLE ----------------*/
  //listens for changes to check status to properly render check or unchecked box
  useEffect(() => {
    let updatedIsChecked = checkStatus;
    setIsChecked(updatedIsChecked);
  }, [checkStatus]);
  /*--------------- HANDLERS ----------------*/
  //Invookes whatever the checkFunction is when clicked
  const clickHandler = () => {
    checkFunction();
  };
  return (
    <div
      className=" __checkbox_container__ w-16 h-16 bg-blue-600 flex justify-center items-center rounded-2xl mr-2"
      onClick={clickHandler}
    >
      <div className="__check_container__ w-16 h-16 flex justify-center items-center ">
        {isChecked ? (
          <BsCheckLg
            className="__check__ animate-quick-bounce"
            color="white"
            size={50}
          />
        ) : (
          <div />
        )}
      </div>
    </div>
  );
};

export default CheckBox;
