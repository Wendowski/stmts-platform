# STMTS — The Quote / v1.1
Selected brand direction: the middle option in the minimalist concept round. This is its rounded vector refinement. Two softly rounded quotation shapes paired with a clear uppercase wordmark. The exact same mark is used in every lockup and icon.

## Files
- logos/: primary horizontal lockup, symbol and outlined wordmark; black/white SVG with transparent PNG exports.
- icons/: opaque 1024-square app icon source and PNG, plus Android adaptive foreground/background sources.
- web/: favicon, common PNG sizes and brand CSS variables.
- docs/: brand tokens, implementation notes and font license.
- STMTS_Quote_Brand_Preview.svg / .png: visual reference sheet.

## Usage
Use black artwork on light surfaces and white on dark. Primary identity is monochrome. Stone is a background/separator color, never small text on white. Do not add green or other accents to the logo. Photography and user content provide color; product UI accents can be specified separately.

Minimum visible symbol height: 24px. Minimum full lockup canvas width: 160px. For smaller browser favicons use the provided icon assets, not the wordmark. Clear space: one stem width on every side, measured from visible edges. Do not stretch, outline, rotate, add shadows, alter the rounded quotation geometry, separate the two quote shapes, or change the relative symbol/wordmark scale.

The name is STMTS (pronounced “statements”). Use that accessible name on the home link; decorative logo images inside a separately named link use empty alt text. Logo-only images elsewhere use alt="STMTS". Do not read the mark as two quotation punctuation characters in assistive labels.

App source has square corners and no transparency; let each platform apply its mask. Android foreground is centered inside an adaptive safe area; validate masks on devices. Store-specific screenshots, asset catalogs and every launcher density must be produced and tested in the actual platform projects.

The PNGs are export conveniences; SVG paths are the authoritative editable sources. Wordmark glyphs are outlined from DejaVu Sans; font attribution/license is included. The identity has not undergone trademark clearance.

This package develops the selected visual direction. It does not modify the application repository or replace existing design/architecture files automatically.
