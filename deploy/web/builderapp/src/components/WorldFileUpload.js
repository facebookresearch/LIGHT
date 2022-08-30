
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Redirect } from "react-router-dom";
import { MenuItem } from "@blueprintjs/core";

function WorldFileUpload({ setPopover }) {
  const inputRef = React.useRef();
  const [file, setFile] = React.useState(undefined);
  return (
    <>
      <input
        onChange={(e) => {
          setFile(undefined);
          const fileReader = new FileReader();
          fileReader.onload = function (event) {
            setFile(JSON.parse(event.target.result));
          };
          const file = e.target.files[0];
          fileReader.readAsText(file);
          setPopover(false);
        }}
        type="file"
        ref={inputRef}
        style={{ display: "none" }}
      />
      {file && (
        <Redirect to={{ pathname: "/world_builder", state: { data: file } }} />
      )}
      <MenuItem
        icon="upload"
        onClick={() => inputRef.current.click()}
        text="Upload File"
        shouldDismissPopover={false}
      />
    </>
  );
}

export default WorldFileUpload;
