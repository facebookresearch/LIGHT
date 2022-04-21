// Tailwind doesn't let you create dynamic classes like `bg-${color}-500`. 
// For convenience, We are adding all color classes to safeList so that we can do this dynamically.
const colors = [
  "slate",
  "gray",
  "zinc",
  "neutral",
  "stone",
  "red",
  "orange",
  "amber",
  "yellow",
  "lime",
  "green",
  "emerald",
  "teal",
  "cyan",
  "sky",
  "blue",
  "indigo",
  "violet",
  "purple",
  "fuchsia",
  "pink",
  "rose",
];
const scales = [
  "50",
  "100",
  "200",
  "300",
  "400",
  "500",
  "600",
  "700",
  "800",
  "900",
];
const types = ["bg", "border", "text"];

// States like hover and focus (see https://tailwindcss.com/docs/hover-focus-and-other-states)
// Add to this list as needed
const states = ["hover"];

const colorSafeList = [];
for (let i = 0; i < types.length; i++) {
  const t = types[i];

  for (let j = 0; j < colors.length; j++) {
    const c = colors[j];

    for (let k = 0; k < scales.length; k++) {
      const s = scales[k];

      colorSafeList.push(`${t}-${c}-${s}`);

      for (let l = 0; l < states.length; l++) {
        const st = states[l];
        colorSafeList.push(`${st}:${t}-${c}-${s}`);
      }
    }
  }
}

colorSafeList.push( 'btn-primary', 'btn-secondary', 'btn-warning')

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: ['@tailwindcss/typography', require("daisyui")],
  daisyui: {
    themes: [{
      dark: {
        ...require("daisyui/src/colors/themes")["[data-theme=dark]"],
        "--rounded-box": "0.375rem",
        "--rounded-btn": "0.375rem",
        "--rounded-badge": "0.375rem",
        "--btn-text-case": "none",
      }
    }]
  },
  safelist: [].concat(colorSafeList),
}
