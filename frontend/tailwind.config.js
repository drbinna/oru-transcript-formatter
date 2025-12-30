/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        oru: {
          navy: '#002F60',
          gold: '#C5B783',
          'gold-dark': '#A28E2A',
        }
      }
    },
  },
  plugins: [],
}
