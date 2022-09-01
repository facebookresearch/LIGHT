/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
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
  plugins: [
    require("daisyui"),
    require('@tailwindcss/typography'),
  ],
};
