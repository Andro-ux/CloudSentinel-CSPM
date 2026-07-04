/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F19',
        surface: '#151C2C',
        surfaceHighlight: '#1E293B',
        primary: '#3B82F6',
        primaryHover: '#2563EB',
        accent: '#10B981',
        danger: '#EF4444',
        warning: '#F59E0B',
        text: '#F8FAFC',
        textMuted: '#94A3B8',
        border: '#334155'
      }
    },
  },
  plugins: [],
}
