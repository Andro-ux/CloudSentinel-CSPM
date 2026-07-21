import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        retro: {
          bg: '#0f0f1b',
          surface: '#1a1a2e',
          surfaceAlt: '#252542',
          border: '#3a3a5c',
          text: '#e0e0ff',
          textMuted: '#8888aa',
          primary: '#00ff9d',
          primaryDim: '#00cc7d',
          secondary: '#ff00ff',
          accent: '#00ffff',
          critical: '#ff0040',
          high: '#ff6600',
          medium: '#ffcc00',
          low: '#00ccff',
          healthy: '#00ff9d',
        },
      },
      fontFamily: {
        retro: ['"Press Start 2P"', 'cursive'],
        mono: ['"Fira Code"', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'retro': '4px 4px 0px 0px rgba(0, 255, 157, 0.3)',
        'retro-sm': '2px 2px 0px 0px rgba(0, 255, 157, 0.2)',
        'glow': '0 0 20px rgba(0, 255, 157, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scanline': 'scanline 8s linear infinite',
      },
      keyframes: {
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
      },
    },
  },
  plugins: [],
}

export default config
