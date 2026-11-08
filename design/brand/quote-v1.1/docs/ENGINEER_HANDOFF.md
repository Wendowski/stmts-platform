# Adopt The Quote identity
1. Treat this selected identity as the brand direction going forward. Preserve the product layout and Markdown behavior unless a separate design decision changes them.
2. Replace prior speech-page/ribbon/S-emblem brand references with logos/lockup-black.svg or lockup-white.svg; use the mark alone in constrained spaces. Do not redraw using a font quotation glyph.
3. Copy assets into the application asset pipeline. Use SVG on Angular, vector-compatible imports on iOS, and vector drawables on Android. Bind logo variant to background luminance/theme. No font runtime dependency for logos.
4. iOS: import icons/app-icon.png into the appropriate app-icon catalog and generate required platform variants with the current Xcode toolchain; do not bake in a rounded mask.
5. Android: place android-foreground.xml as drawable/stmts_foreground.xml and android-background.xml as drawable/stmts_background.xml; place adaptive XML into the appropriate mipmap-anydpi-v26 resource. Move the monochrome entry to a v33-qualified adaptive resource if required by the project configuration. Generate legacy launcher assets separately. No native resource build has been run here.
6. Verify light/dark headers, 24px visible mark, compact lockup, favicon, Android circular/squircle masks and iOS icon appearance on real devices. Ensure brand is not mistaken for a quote action inside the composer: logo goes only in identity/navigation context.
7. Record adoption in the actual application repository with a focused commit. This standalone pack is not that repository and makes no claim to have changed it.

Product fonts can remain platform system fonts. The outlined logo does not require bundling or installing DejaVu Sans in the app.
