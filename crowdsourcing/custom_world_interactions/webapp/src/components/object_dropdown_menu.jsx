/*
 * Copyright (c) 2017-present, Facebook, Inc.
 * All rights reserved.
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

import React from "react";
import DropdownButton from 'react-bootstrap/DropdownButton';
import Dropdown from 'react-bootstrap/Dropdown';

function ObjectDropdown() {
      return (
        <Dropdown>
          <Dropdown.Toggle variant="success" id="dropdown-basic">
            Select Object
          </Dropdown.Toggle>

          <Dropdown.Menu>
            <Dropdown.Item href="#/action-1">Object 1</Dropdown.Item>
            <Dropdown.Item href="#/action-2">Object 2</Dropdown.Item>
            <Dropdown.Item href="#/action-3">Object 3</Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      );
}

export { ObjectDropdown };
