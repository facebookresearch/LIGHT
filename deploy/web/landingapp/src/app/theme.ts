/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/**
 * Get the corresponding daisyui theme class for say/do/tell/etc actions
 * @param where The location such as "bg", "text", "border-r"
 * @param action The action such as "say", "do", "tell"
 * @param autoTextStyle If true, the text color will be automatically set to light or dark depending on the theme background color
 * @returns daiysui theme class
 */
export function getActionThemeColor(
  where: string,
  action: string,
  autoTextStyle: boolean = true
): string {
  const actionColors: any = {
    say: "accent",
    tell: "info",
    do: "warning",
    default: "base-100",
    theySay: "white",
    theyDo: "red-100"
  };

  const color = actionColors[action] || actionColors.default;
  console.log("color:  ", color)
  const postfix = where === "text" && autoTextStyle ? "-content" : "";
  console.log("postfix:  ", postfix)
  // To build a class dynamically, this requires the theme classes be in safeList first. See tailwind.config.js.
  console.log("THEME RETURN RESULT:  ", `${where}-${color}${postfix}`)
  return `${where}-${color}${postfix}`;
}
