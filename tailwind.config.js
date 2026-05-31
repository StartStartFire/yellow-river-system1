/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        'tech-bg': '#0a1929',
        'tech-card': '#112536',
        'tech-border': '#1a3a52',
        'tech-primary': '#00d4ff',
        'tech-secondary': '#0088cc',
        'tech-text': '#e0e6ed',
        'tech-muted': '#7a8fa3'
      },
      screens: {
        'xl': '1920px'
      }
    }
  },
  plugins: []
}
