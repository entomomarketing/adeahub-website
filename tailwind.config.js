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
      // Sections that widen with the window, as on adeahub.co (its Elementor containers are a share of the screen).
      // Each is the section's fixed width up to about 1440px and the live site's share of the window above it, so
      // wide screens get live's proportions and smaller laptops keep the fixed layout.
      maxWidth: {
        'fluid-hero': 'max(1200px, calc(80vw + 48px))',    // product heroes (px-6): content 80% of the window
        'fluid-section': 'max(1188px, calc(80vw + 28px))', // card bands (px-6): content 80% of the window less 20px
        'fluid-wide': 'max(1296px, 90vw)',                 // homepage "One platform" stage and hospital strip
        'fluid-narrow': 'max(772px, calc(55vw - 20px))',   // AH Insights "Predictive intelligence" heading and cards
      },
      boxShadow: {
        soft: '0 10px 40px -10px rgba(0,0,0,0.08)',
        floating: '0 24px 60px -16px rgba(82,152,248,0.18), 0 8px 24px -8px rgba(0,0,0,0.06)',
      },
    },
  },
};
