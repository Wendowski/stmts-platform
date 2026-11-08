# ADR 0003: Adopt rounded Quote identity

8 November 2026. Reviewed the supplied `STMTS_Quote_Brand_v1(1).zip`: package README, engineering handoff, tokens, changelog and preview. Internal version is 1.1, the rounded refinement of the selected Quote identity.

Preserve the package unchanged under `design/brand/quote-v1.1/` and the original design kit under `design/reference/`. The newer selected identity replaces the speech-page mark, not the Paper / Forest reading layout, product typography or UI accent palette.

Angular uses authoritative black/white SVG lockups on corresponding light/dark surfaces and the exact mark at compact widths. The home link has accessible name STMTS; logo images are decorative inside it. The full lockup canvas is 184px wide (above the 160px minimum); compact mark is 44px square (visible artwork above 24px), with additional padding for stem-width clear space. Provided favicon and touch icon replace default references. No logo recoloring, redrawing or runtime font dependency.

Native icon/adaptive sources and the font license are retained in the reference package. Native catalogs, legacy launcher variants, actual mask checks and device validation belong to native tasks 4–7 and are not claimed complete here. Browser visual verification remains outstanding; compilation/SSR verify integration only.
