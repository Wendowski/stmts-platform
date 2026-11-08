# Engineering references
Consulted 8 November 2026. Product limits, visual tokens and implementation choices in this kit are STMTS proposals. Official guidance informs accessibility and security; it does not certify this kit or the future app.

- WCAG 2.2: https://www.w3.org/TR/WCAG22/ — web conformance and reflow, focus, contrast, target requirements.
- W3C contrast explanation: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum — normal text 4.5:1 and large text 3:1.
- Apple HIG: https://developer.apple.com/design/human-interface-guidelines/ — native conventions.
- Apple Dynamic Type: https://developer.apple.com/videos/play/wwdc2024/10074/ — text scaling and layout adaptation.
- Android accessibility: https://developer.android.com/guide/topics/ui/accessibility/apps — minimum 48dp interactive targets and assistive use.
- CommonMark: https://spec.commonmark.org/0.31.2/ — baseline syntax. STMTS intentionally restricts HTML and adds explicitly listed extensions.
- Angular security: https://angular.dev/best-practices/security — safe bindings, sanitization and avoiding unsafe trust bypasses.

The 44px web target is a stricter STMTS design choice than the WCAG 2.2 AA 24px minimum (subject to its exceptions). Do not confuse the proposed product baseline with the standard's minimum.
