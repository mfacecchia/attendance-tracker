/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./static/script/*.js", "./templates/*.html"],
  theme: {
    extend: {
      keyframes: {
        'hide': {
          '0%': { opacity: '1' },
          '99%': { visibility: 'hidden' },
          '100%': { opacity: '0' }
        }
      },
      animation: {
        'hide': 'hide 200ms ease-in-out forwards 5s'
      },
      colors: {
        'attendance-blue': {
          100: '#CEE7FF',
          700: '#002755'
        },
        'carbon': '#1E1E1E'
      },
      borderWidth: {
        '1.5': '1.5px'
      }
    },
  },
  plugins: [],
}

