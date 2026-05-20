---
name: Ethereal Ink
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#5a413c'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#8e706a'
  outline-variant: '#e2bfb8'
  surface-tint: '#b12c14'
  primary: '#a5230c'
  on-primary: '#ffffff'
  primary-container: '#c83c23'
  on-primary-container: '#ffefeb'
  inverse-primary: '#ffb4a5'
  secondary: '#3d6658'
  on-secondary: '#ffffff'
  secondary-container: '#bce9d7'
  on-secondary-container: '#416b5c'
  tertiary: '#735c00'
  on-tertiary: '#ffffff'
  tertiary-container: '#cca72f'
  on-tertiary-container: '#4e3d00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad3'
  primary-fixed-dim: '#ffb4a5'
  on-primary-fixed: '#3e0400'
  on-primary-fixed-variant: '#8e1300'
  secondary-fixed: '#bfecda'
  secondary-fixed-dim: '#a3d0be'
  on-secondary-fixed: '#002118'
  on-secondary-fixed-variant: '#244e41'
  tertiary-fixed: '#ffe088'
  tertiary-fixed-dim: '#e9c349'
  on-tertiary-fixed: '#241a00'
  on-tertiary-fixed-variant: '#574500'
  background: '#fcf9f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
  misty-white: '#F5F5F3'
  ink-black: '#1A1A1A'
  cinnabar-red: '#C83C23'
  jade-green: '#4F796A'
  silk-gold: '#D4AF37'
typography:
  display-hero:
    fontFamily: Noto Serif
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 60px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Noto Serif
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Noto Serif
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Noto Serif
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.05em
  caption:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  section-gap: 80px
---

## Brand & Style
The design system embodies the "New Chinese" aesthetic, a sophisticated fusion of traditional Eastern artistry and contemporary digital precision. It is designed for a creative, primarily female audience (authors, Hanfu enthusiasts, and dreamers) who seek an emotional connection to cultural heritage through AI.

The visual direction is **Minimalist-Guofeng**: it utilizes heavy whitespace to evoke the "Liu Bai" (leaving blank) technique of classical ink paintings, paired with **Glassmorphism** to represent the ethereal, misty quality of "Xianxia" (immortal hero) themes. The atmosphere is premium, dreamy, and culturally profound, moving away from utilitarian tool design toward a curated "Fantasy Studio" experience.

## Colors
The palette is rooted in the "Five Colors" of Chinese tradition but filtered through a modern lens.
- **Misty White (#F5F5F3):** The primary background color. It is warmer and softer than pure white, mimicking the texture of aged rice paper or silk.
- **Ink Black (#1A1A1A):** Used for primary typography and structural borders. It provides a deep, grounding contrast to the ethereal backgrounds.
- **Cinnabar Red (#C83C23):** The primary action color. Use this for CTAs, critical status indicators, and traditional "Seal" elements.
- **Jade Green (#4F796A):** A secondary accent used for secondary actions, subtle highlights, and organic elements to evoke a sense of calm and refinement.
- **Silk Gold (#D4AF37):** Reserved for premium tiers, borders of high-value cards, and delicate decorative linework.

## Typography
The typographic system pairs the authoritative, literary grace of **Noto Serif** (Songti style) with the welcoming clarity of **Plus Jakarta Sans**. 

Headlines should utilize Noto Serif to establish a "Guofeng" cultural tone. For display text, increased letter spacing and vertical orientations (where appropriate for decorative sidebars) are encouraged. All functional UI elements, labels, and body descriptions use Plus Jakarta Sans to ensure maximum readability and a modern "SaaS" feel. Large display headings should be reduced for mobile screens to maintain a balanced composition.

## Layout & Spacing
The system uses a **Fixed Grid** model for desktop to maintain a gallery-like, curated feel, centering the content at a maximum width of 1280px. 

A 12-column grid is used for the workspace, allowing for a 4-column sidebar for parameters and an 8-column main stage for generation results. We emphasize generous "Liu Bai" (negative space) between sections (80px+) to prevent the interface from feeling cluttered or overly technical. On mobile, the layout reflows to a single column with 16px side margins. Padding within glassmorphic panels should be consistent (24px) to maintain the airy, lightweight aesthetic.

## Elevation & Depth
Depth is created through **Tonal Layers** and **Glassmorphism** rather than heavy shadows.
- **Base Layer:** Misty White (#F5F5F3) solid background.
- **Surface Layer (Panels/Cards):** White surfaces with 60-80% opacity and a 20px backdrop-blur. These represent "misty" layers floating over the paper base.
- **Ink-Wash Shadows:** Instead of standard gray shadows, use soft, diffused shadows with a slight tint of Ink Black (#1A1A1A) at very low opacity (5-8%) to mimic ink bleeding into paper.
- **Decorative Elevation:** Use Silk Gold (#D4AF37) 1px strokes for high-priority cards (e.g., active style selection) to give them a "lifted" or "framed" appearance.

## Shapes
The shape language is organic and soft, avoiding sharp technical corners. 
- **Standard UI Elements:** Use a 0.5rem (8px) radius for buttons and input fields.
- **Content Containers:** Style cards and image containers use `rounded-lg` (16px) or `rounded-xl` (24px) to create a friendly, approachable aesthetic.
- **Decorative Motifs:** Circular frames for avatars or "Seal" style square buttons for specialized actions (like "Randomize") are encouraged to reinforce the cultural theme.

## Components
- **Buttons:** Primary buttons use Cinnabar Red with white text. Secondary buttons use a Glassmorphic style (misty white background with a thin Ink Black border).
- **Style Cards:** These are the centerpiece. Use high-quality imagery with a vertical text label overlay (Noto Serif). Active states are indicated by a 1px Silk Gold border and a subtle "ink-wash" shadow.
- **Input Fields:** Minimalist design. Only a bottom border in Ink Black (20% opacity) that turns to Jade Green on focus.
- **Chips/Labels:** Small, rounded-pill shapes with Misty White backgrounds and Jade Green text, used for tags like "Tang Style" or "HD."
- **Glass Panels:** Used for the "Generation Workspace" parameter controls. High blur (24px) and 70% opacity allow the background art to subtly peek through.
- **The "Seal" CTA:** The main "Generate" action should incorporate a subtle texture overlay or a square border motif reminiscent of a traditional Chinese stone seal.