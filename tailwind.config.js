/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#096b9f",
          contrast: "#f8fbff",
        },
        emerald: {
          50: "#e6f2f9",
          100: "#c7e1f3",
          200: "#98c6e7",
          300: "#6ba8d6",
          400: "#3f89c2",
          500: "#096b9f",
          600: "#075a84",
          700: "#05486a",
          800: "#033750",
          900: "#02263a",
          950: "#011928",
        },
      },
      fontFamily: {
        display: ["Poppins", "ui-sans-serif", "system-ui"],
        body: ["Inter", "ui-sans-serif", "system-ui"],
      },
      boxShadow: {
        glow: "0 0 30px rgba(56, 189, 248, 0.45)",
      },
    },
  },
  plugins: [],
};
