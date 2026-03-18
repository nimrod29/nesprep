/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#FFF8F0",
          100: "#F5EFE6",
          200: "#EAD9C2",
          300: "#E4D3BD",
          400: "#D4B896",
          500: "#E2A94B",
          600: "#C9922E",
          700: "#A07524",
          800: "#6E5B47",
          900: "#5B4A3A",
          950: "#3D2F25",
        },
        sidebar: {
          DEFAULT: "#2C2218",
          surface: "#3D2F25",
          border: "#4D3D30",
          text: "#D4C4B0",
        },
      },
    },
  },
  plugins: [],
};
