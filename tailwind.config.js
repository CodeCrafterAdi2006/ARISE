/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'absolute-black': '#050202',
        'deep-obsidian': '#0D0707',
        'blazing-crimson': '#FF0033',
        'runic-amber': '#FF5500',
        'muted-crimson': '#990000',
      },
      boxShadow: {
        'crimson-glow': '0 0 10px rgba(255, 0, 51, 0.5), 0 0 20px rgba(255, 0, 51, 0.3), inset 0 0 10px rgba(255, 0, 51, 0.2)',
        'runic-glow': '0 0 15px rgba(255, 85, 0, 0.6), 0 0 30px rgba(255, 0, 51, 0.4)',
      },
      fontFamily: {
        'display': ['"Space Grotesk"', 'sans-serif'],
        'body': ['"Inter"', 'sans-serif'],
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'particle-float': 'particle-float 15s infinite linear',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: 1, filter: 'brightness(1)', transform: 'scale(1)' },
          '50%': { opacity: 0.8, filter: 'brightness(1.5)', transform: 'scale(1.02)' },
        },
        'particle-float': {
          '0%': { transform: 'translateY(0) scale(1)', opacity: 0 },
          '10%': { opacity: 0.8 },
          '90%': { opacity: 0.8 },
          '100%': { transform: 'translateY(-100vh) scale(0.5)', opacity: 0 },
        }
      }
    },
  },
  plugins: [],
}
