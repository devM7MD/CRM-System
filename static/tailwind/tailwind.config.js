// tailwind.config.js
module.exports = {
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
          sans: ['Inter', 'sans-serif'],
          heading: ['Poppins', 'sans-serif'],
        },
        boxShadow: {
          card: '0 4px 6px rgba(0, 0, 0, 0.05)',
          sidebar: '0 0 10px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    variants: {},
    plugins: [],
  }