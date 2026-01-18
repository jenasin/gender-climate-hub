/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'unwomen': '#E91E63',
        'worldbank': '#2196F3',
        'undp': '#00BCD4',
        'climate': '#4CAF50',
        'who': '#03A9F4',
        'ilo': '#FF9800',
      }
    },
  },
  plugins: [],
}
