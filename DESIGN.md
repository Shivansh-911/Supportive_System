---
name: Midnight Amethyst
colors:
  surface: '#161121'
  surface-dim: '#161121'
  surface-bright: '#3c3648'
  surface-container-lowest: '#100b1b'
  surface-container-low: '#1e1929'
  surface-container: '#221d2e'
  surface-container-high: '#2d2739'
  surface-container-highest: '#383244'
  on-surface: '#e9def6'
  on-surface-variant: '#cec3d3'
  inverse-surface: '#e9def6'
  inverse-on-surface: '#332e3f'
  outline: '#978d9d'
  outline-variant: '#4c4452'
  surface-tint: '#ddb8ff'
  primary: '#ddb8ff'
  on-primary: '#490081'
  primary-container: '#c084fc'
  on-primary-container: '#500989'
  inverse-primary: '#7b41b4'
  secondary: '#afcbd8'
  on-secondary: '#19343e'
  secondary-container: '#334d58'
  on-secondary-container: '#a1bdca'
  tertiary: '#c3c0ff'
  on-tertiary: '#272377'
  tertiary-container: '#9896ef'
  on-tertiary-container: '#2d2a7d'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#f0dbff'
  primary-fixed-dim: '#ddb8ff'
  on-primary-fixed: '#2c0051'
  on-primary-fixed-variant: '#62259b'
  secondary-fixed: '#cbe7f5'
  secondary-fixed-dim: '#afcbd8'
  on-secondary-fixed: '#021f29'
  on-secondary-fixed-variant: '#304a55'
  tertiary-fixed: '#e2dfff'
  tertiary-fixed-dim: '#c3c0ff'
  on-tertiary-fixed: '#100563'
  on-tertiary-fixed-variant: '#3e3c8f'
  background: '#161121'
  on-background: '#e9def6'
  surface-variant: '#383244'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
---

## Brand & Style
The design system embodies a "Boutique Creative" aesthetic—a blend of high-end editorial sophistication and modern digital fluidity. It targets creative professionals, independent studios, and premium service providers who value a calm, immersive environment that fosters focus and inspiration.

The visual narrative is built on **Sophisticated Minimalism** with **Glassmorphic** accents. It avoids the harshness of typical dark modes by using deep, chromatic purples instead of pure blacks, creating a "velvet" atmosphere. The emotional response is one of quiet confidence, prestige, and mystery. Design elements should feel like they are floating in a deep, atmospheric space, utilizing soft glows and subtle gradients to define boundaries rather than hard lines.

## Colors
The palette is centered around **Deep Eggplant (#0f0a1a)**, which serves as the canvas. This is not a flat neutral but a saturated dark tone that adds depth to the UI. 

- **Primary (Soft Lavender):** Used for key actions, brand moments, and active states. It should frequently be applied as a soft glow or a linear gradient (Lavender to a deeper violet) to maintain the "boutique" feel.
- **Secondary (Cool Slate):** Acts as a grounding element for utility icons, de-emphasized text, and secondary borders, preventing the UI from feeling overly "neon."
- **Tertiary (Indigo):** Reserved for subtle background gradients and deep shadows to add layered dimension.
- **Surface Strategy:** Use semi-transparent overlays and background blurs (10px–20px) on top of the eggplant base to create a sense of physical layering.

## Typography
This design system utilizes **Inter** exclusively to achieve a systematic, clean look that balances the expressive color palette. 

The typographic hierarchy relies on tight tracking and leading for headlines to create a "locked-in" editorial feel. Body text maintains generous line height (1.5x–1.6x) to ensure legibility against the dark background. Labels are often set in uppercase with slight letter spacing to act as structural anchors within the layout. For high-contrast moments, use the Primary Lavender color for headlines or key pull-quotes.

## Layout & Spacing
The layout follows a **Fluid Grid** philosophy with generous outer margins to emphasize the boutique, spacious feel. 

- **Desktop:** 12-column grid with 64px side margins. Elements should feel grouped in logical clusters with significant whitespace (80px+) between major sections.
- **Mobile:** 4-column grid with 16px margins.
- **Rhythm:** All spacing must be a multiple of 8px. Use "Airy" padding (md and lg units) within cards and containers to maintain the calm, sophisticated atmosphere. Avoid crowding elements; when in doubt, increase the spacing unit.

## Elevation & Depth
Depth is created through **Tonal Layering** and **Subtle Glows** rather than traditional black shadows.

1.  **Base:** Deep Eggplant (#0f0a1a).
2.  **Level 1 (Cards/Sections):** A slightly lighter purple-tinted surface (#1a1329) with a 1px border at 10% white opacity.
3.  **Level 2 (Modals/Popovers):** Surface-glass with a 40px backdrop blur and a thin "top-down" highlight border (white at 15% opacity).
4.  **Shadows:** Use "Amethyst Shadows"—diffused blurs using the primary Lavender color at very low opacity (5-8%) to suggest a light source emitting from the components themselves.

## Shapes
The shape language is consistently **Rounded (8px base)**. This creates a soft, approachable feel that contrasts with the technical nature of the Inter typeface.

- **Standard Elements:** (Buttons, Inputs, Small Cards) use 8px (`rounded-md`).
- **Large Containers:** (Main Feature Cards, Modals) use 16px (`rounded-lg`).
- **Accent Elements:** (Tags, Pills) use full rounding (999px) to provide visual variety and a "softer" touch.

## Components
- **Buttons:** Primary buttons use a linear gradient from Lavender (#c084fc) to a slightly deeper violet. Text is dark eggplant for high contrast. Secondary buttons are ghost-style with a Cool Slate border.
- **Inputs:** Fields are dark with a 1px Cool Slate border. On focus, the border transitions to Lavender with a subtle 4px outer glow.
- **Cards:** Use a "Glass-Dark" effect. Background is `#1a1329` at 80% opacity with a 20px blur. 1px stroke around the card using a gradient: white (10%) to transparent.
- **Chips/Tags:** Small, pill-shaped with a Tertiary Indigo background and Lavender text.
- **Progress Indicators:** Use the Primary Lavender color, ideally with a soft "bloom" or neon-like outer glow to make them pop against the dark background.
- **Lists:** Separated by thin 1px lines in Cool Slate at 20% opacity. Interactive list items should have a subtle Lavender hover state at 5% opacity.