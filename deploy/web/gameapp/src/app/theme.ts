
/**
 * Get the corresponding daisyui theme class for say/do/tell/etc actions
 * @param where The location such as "bg", "text", "border-r"
 * @param action The action such as "say", "do", "tell"
 * @returns daiysui theme class
 */
export function getActionThemeColor(where:string, action:string) {
  const actionColors:any = {
    say: "accent",
    tell: "info",
    do: "success",
    default: "base"
  };
  
  const color = actionColors[action] || actionColors.default;
  const postfix = (where === "text") ? "-content" : "";

  // To build a class dynamically, this requires the theme classes be in safeList first. See tailwind.config.js.
  return `${where}-${color}${postfix}`;
}