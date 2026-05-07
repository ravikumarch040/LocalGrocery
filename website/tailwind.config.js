/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts}'],
  theme: {
    extend: {
      colors: {
        leaf: {
          50: '#f2f9f4',
          100: '#dcefe2',
          200: '#b9dfca',
          300: '#8ac7a8',
          400: '#58a67d',
          500: '#368760',
          600: '#276c4d',
          700: '#1f5640',
          800: '#1a4435',
          900: '#16382d',
        },
        cream: {
          50: '#fdfbf7',
          100: '#faf6ed',
          200: '#f3e9d6',
          300: '#e8d4b3',
        },
        citrus: {
          400: '#f5b83c',
          500: '#ea9a1a',
          600: '#cc7a0f',
        },
        ink: '#1b1f1c',
      },
      fontFamily: {
        display: ['Sora', 'system-ui', 'sans-serif'],
        sans: ['Source Sans 3', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 22px 60px -24px rgba(22, 56, 45, 0.35)',
        card: '0 12px 40px -20px rgba(27, 31, 28, 0.22)',
      },
      backgroundImage: {
        grain:
          "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='128' height='128'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E\")",
      },
    },
  },
  plugins: [],
}
