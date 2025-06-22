/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',//template at the project level
    './**/templates/**/*.html'//templates inside apps folder
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

