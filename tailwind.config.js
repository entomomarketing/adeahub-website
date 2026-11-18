/** Tailwind CSS v3 configuration — compiled by `python3 tools/build.py` with the standalone CLI (no npm). */
module.exports = {
  content: ['./public/**/*.html', '!./public/embeds/**', './public/assets/js/**/*.js', './tools/chrome.py'],
  theme: {
    extend: {
      fontFamily: { sans: ['Outfit', 'sans-serif'] },
      colors: {
        adeahub: {
          blue: '#5298F8', yellow: '#F3D06F', gray: '#4B5563', lightbg: '#5298F8',
          // Text versions of the brand blue that meet WCAG AA contrast on white and the pale-blue tints:
          heading: '#408DF7', // large text (>= 24px, or >= 18.66px bold): 3:1
          ink: '#186BDC',     // body-size text, labels, links: 4.5:1
        },
      },
      boxShadow: {
        soft: '0 10px 40px -10px rgba(0,0,0,0.08)',
        floating: '0 24px 60px -16px rgba(82,152,248,0.18), 0 8px 24px -8px rgba(0,0,0,0.06)',
      },
    },
  },
};
