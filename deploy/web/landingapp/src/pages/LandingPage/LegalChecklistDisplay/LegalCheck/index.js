/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/* REACT */
import React, { useState, useEffect } from "react";

const LegalCheck = ({ itemIndex, responses, legalItem, responseHandler }) => {
  const [isChecked, setIsChecked] = useState(false);

  /*--------------- LIFECYLCLE ----------------*/
  useEffect(() => {
    let updatedValue = responses[itemIndex];
    setIsChecked(updatedValue);
  }, [responses]);
  /*--------------- HANDLERS ----------------*/

  return (
    <div className="flex items-start text-white">
      <div className="form-control">
        <label className="cursor-pointer label">
          <input
            type="checkbox"
            checked={isChecked}
            onChange={responseHandler}
            className="checkbox checkbox-accent"
          />
          <span>{legalItem}</span>
        </label>
      </div>
    </div>
  );
};

export default LegalCheck;
