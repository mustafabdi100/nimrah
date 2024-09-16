/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './shop/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'custom-gold': '#D39901',
        'custom-banner': '#D39901',
        'footer-bg': '#f3f3f3',
        'footer-text': '#333',
      },
      fontFamily: {
        serif: ['Playfair Display', 'serif'],
        sans: ['Lato', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
