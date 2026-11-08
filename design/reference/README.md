# STMTS — design and engineering handoff · v1.0

Start with `DESIGN_GUIDE.md`, then `spec/PRODUCT_SPEC.md`, `spec/ACCEPTANCE.feature`, and `spec/BUILD_ORDER.md`. Open `concepts/index.html` locally for the visual concept board and `concepts/app.html` for responsive screen studies. These are framework-independent design references, not a production app. The gallery offers three visual directions; **01 Paper / Forest** is the implementation baseline.

## Package map
- `styles/stmts.css`: reusable semantic tokens, controls, post cards, and Markdown prose styles.
- `tokens/design-tokens.json`: machine-readable source of truth for color, spacing, type, layout, motion, touch sizes.
- `assets/`: original vector brand mark, outlined wordmark, 15 icons, two demo cover illustrations; PNG app icon and cover exports.
- `concepts/`: desktop feed, long-form reader, composer, profile, mobile/tablet, dark theme, alternative directions, PNG and editable SVG concept exports. `media-and-states.png` adds gallery/video/upload-state guidance.
- `angular/`: illustrative standalone component and typed contracts to integrate into a real Angular project.
- `native/`: SwiftUI and Jetpack Compose token examples and adaptation notes.
- `spec/`: normative requirements, acceptance scenarios, content model, implementation sequence, source references.

## How to preview
Open `concepts/index.html` in a browser. No installation, fonts, analytics, external requests, account, or server required. All sample content is fictional. Navigation, theme changes, reading views, and composer mode changes are local demonstrations. Publishing, uploads, persistence, search, and authentication are specified but not implemented.

## Precedence
Requirements with IDs in PRODUCT_SPEC.md are normative. design-tokens.json owns numeric values; styles implement them. Screen studies illustrate hierarchy, not fixed heights. Native controls follow platform behavior. If visual reference and normative requirement conflict, follow the requirement and log the discrepancy.

Scope: an implementation-ready design baseline and starter assets. Backend, full native projects, production Angular build, final store icon sets, security audit, and end-to-end application verification are future engineering work. Version and dependency selections belong to the application repository.
