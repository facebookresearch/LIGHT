/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

export function zipToObject(keys, values) {
  return keys.reduce((obj, k, i) => ({ ...obj, [k]: values[i] }), {});
}

export function setCaretPosition(elem, caretPos) {
  /* inspired from: https://stackoverflow.com/a/512542 */
  if (elem != null) {
    if (elem.createTextRange) {
      var range = elem.createTextRange();
      range.move("character", caretPos);
      range.select();
    } else {
      if (elem.selectionStart) {
        elem.focus();
        elem.setSelectionRange(caretPos, caretPos);
      } else elem.focus();
    }
  }
}
