/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        healthy: '#10B981', // emerald-500
        moderate: '#F59E0B', // amber-500
        unhealthy: '#EF4444', // red-500
        food: '#F97316', // orange-500
      }
    },
  },
  plugins: [],
}
