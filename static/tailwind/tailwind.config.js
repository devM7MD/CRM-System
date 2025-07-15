// tailwind.config.js
module.exports = {
  content: [
    './templates/**/*.html',
    './dashboard/templates/**/*.html',
    './callcenter/templates/**/*.html',
    './delivery/templates/**/*.html',
    './finance/templates/**/*.html',
    './followup/templates/**/*.html',
    './inventory/templates/**/*.html',
    './landing/templates/**/*.html',
    './orders/templates/**/*.html',
    './packaging/templates/**/*.html',
    './products/templates/**/*.html',
    './roles/templates/**/*.html',
    './sellers/templates/**/*.html',
    './settings/templates/**/*.html',
    './sourcing/templates/**/*.html',
    './subscribers/templates/**/*.html',
    './warehouse/templates/**/*.html',
    './warehouse_inventory/templates/**/*.html',
    './**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FFCC00',
        secondary: '#333333',
        background: '#FFFFFF',
        gray: {
          light: '#F8F9FA',
          medium: '#E9ECEF',
        },
      },
      fontFamily: {
        sans: ['Cairo', 'Inter', 'sans-serif'],
        heading: ['Cairo', 'Poppins', 'sans-serif'],
        arabic: ['Cairo', 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 6px rgba(0, 0, 0, 0.05)',
        sidebar: '0 0 10px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  variants: {},
  plugins: [require('tailwindcss-rtl')],
}