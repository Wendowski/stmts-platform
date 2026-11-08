# Implementation status — 8 November 2026

M0 foundation: **in progress**. M1 read-only rendering: **in progress**. Neither milestone meets its full exit gate.

| Requirement | Implementation | Evidence / remaining gate |
|---|---|---|
| ARC-001/002; M0 | Django/DRF, initial versioned GET contract, generated TypeScript transport types | Parser/API tests and Angular production build pass; no persistent models yet |
| M0 repository/toolchain | Web and Python locks; service configuration; CI; original design kit | Native locks, native builds and Docker startup unverified |
| MD-001/004/007; CONTENT-001/003 | Canonical node parser, escaped text bindings, safe URL checks; no HTML trust bypass | 11 shared source fixtures exercised; rich native rendering and final dialect conformance incomplete |
| MD-002; FEED-002 | Unicode source length, parser nesting/block bounds, excerpt/read time | Source-boundary tests pass; complete per-variant schema limits pending |
| CONTENT-002 | Prototype strict-property recursive node schema and content-based block IDs | Schema validation passes; discriminated variants, media/tasks and stable duplicate-block matching pending |
| READ-001; UI-001 | Angular responsive card/reader and Paper / Forest colors, table/code containers, TOC | Compiled; API-backed card and reader text verified in SSR HTML. Browser layout and TOC threshold refinement pending |
| A11Y-001–004 | Semantic headings, skip link, labels, focus rings, reflow CSS | No browser, zoom, screen-reader, RTL or native-device acceptance evidence yet |
| M1 native | SwiftUI package plus XcodeGen app definition; Compose Android scaffold; shared post JSON | Uncompiled text projections. Rich inline/list/table/link parity, theme integration and native contract generation pending |
| REL-002/003 | Original ACCEPTANCE.feature preserved; test coverage separated from release gates | Full acceptance suite not executed; no external-beta readiness claim |

## Exact verification

- `STMTS_DEVELOPMENT=1 .venv/bin/pytest -q -c stmts/pytest.ini`: **20 passed**. Includes 11 source fixtures, URL safety, Unicode limit, stable paragraph ID, code exclusion from reading time and development API/production denial behavior.
- `npm --prefix stmts/web run build`: **passed**, Angular browser and server bundles generated. Static development JSON excluded from production assets.
- `npx openapi-typescript ../contracts/openapi.yaml -o src/app/api.generated.ts`: **passed**; app imports generated model aliases.
- Production Express SSR + development fixture API: **passed**; GET `/` includes card title and GET `/?reader=1` includes rendered body text. Reproducible via `.venv/bin/python tests/verify_ssr.py` from repository root after building.
- `node tests/web-smoke.cjs`: **blocked before browser launch** because Chromium is absent. Installation failed with a truncated browser archive. No screenshots or viewport/visual pass are claimed.
- Native compilation/device tests: **not run**, Xcode/Swift, Gradle/Android SDK unavailable.
- PostgreSQL constraints/concurrency, Redis/broker/worker delivery: **not run / not implemented**. The initial fixture endpoint needs no database.
- Initial build caught and fixed a malformed table template. Initial SSR check caught an empty CSR response; root routing and explicit localhost SSR host allowance were fixed before the successful check.

## Next reviewable work

1. Finish discriminated canonical schema, task/media representation and parser conformance with expected canonical fixture trees.
2. Complete native rich renderers and generated contracts; compile on Apple/Android toolchains and add native CI.
3. Run the visual/accessibility matrix and correct any issues before calling M1 complete.
4. Proceed to M2 persistent public reading and verified identity, then M3 drafts and publication transactions.

Public deployment, real authentication, publishing, reactions, moderation, media uploads and store distribution are not implemented in this increment. Release policy decisions in the architect specification remain open.
