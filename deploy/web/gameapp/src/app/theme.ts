
/**
 * Get the corresponding daisyui theme class for say/do/tell/etc actions
 * @param where The location such as "bg", "text", "border-r"
 * @param action The action such as "say", "do", "tell"
 * @param autoTextStyle If true, the text color will be automatically set to light or dark depending on the theme background color
 * @returns daiysui theme class
 */
export function getActionThemeColor(where:string, action:string, autoTextStyle:boolean = true):string {
  const actionColors:any = {
    say: "accent",
    tell: "info",
    do: "warning",
    default: "base-100",
    theySay: "white",
    theyDo: "red-100",
    theyTell: "info"
  };
  
  const color = actionColors[action] || actionColors.default;
  const postfix = (where === "text" && autoTextStyle) ? "-content" : "";

  // To build a class dynamically, this requires the theme classes be in safeList first. See tailwind.config.js.
  return `${where}-${color}${postfix}`;
}



//#f2e2d2