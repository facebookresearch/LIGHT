
/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//GetWindowDimensions - function that will get and format dimensions of window for purposes of adding them to a components state.
const GetWindowDimensions = () =>{
    const { innerWidth: width, innerHeight: height } = window;
    return {
        width,
        height
    };
}

export default GetWindowDimensions;
