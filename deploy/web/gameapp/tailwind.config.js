/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const defaultTheme = require('tailwindcss/defaultTheme')

// We are adding all color classes to safeList
const colors = [
  "primary",
  "primary-focus",
  "primary-content",
  "secondary",
  "secondary-focus",
  "secondary-content",
  "accent",
  "accent-focus",
  "accent-content",
  "neutral",
  "neutral-focus",
  "neutral-content",
  "base-100",
  "base-200",
  "base-300",
  "base-content",
  "info",
  "info-content",
  "success",
  "success-content",
  "warning",
  "warning-content",
  "error",
  "error-content",
];

const types = ["bg", "border", "text", "border-l", "border-r", "border-t", "border-b", "fill", "stroke"];

// States like hover and focus (see https://tailwindcss.com/docs/hover-focus-and-other-states)
// Add to this list as needed
const states = ["hover"];

const colorSafeList = [];
for (let i = 0; i < types.length; i++) {
  const t = types[i];

  for (let j = 0; j < colors.length; j++) {
    const c = colors[j];
    colorSafeList.push(`${t}-${c}`);

    for (let l = 0; l < states.length; l++) {
      const st = states[l];
      colorSafeList.push(`${st}:${t}-${c}`);
    }
  }
}

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['"Inter"', ...defaultTheme.fontFamily.sans],
        'mono': ['"JetBrains Mono"', ...defaultTheme.fontFamily.mono],
      },
      typography: {
        DEFAULT: {
          css: {
            p: {
              lineHeight: "1.4",
              margin: "1rem 0"
            }
          }
        }
      }
    }
  },
  daisyui: {
    themes: [
      { 
        "light": {
          ...require("daisyui/src/colors/themes")["[data-theme=light]"],
          "success": "#22cc55"
        }
      }
    ]
  },
  plugins: [
    require("daisyui"),
    require('@tailwindcss/typography'),
  ],
  safelist: [].concat(colorSafeList),
};
