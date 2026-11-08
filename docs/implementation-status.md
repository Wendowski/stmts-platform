# Implementation status — 8 November 2026

M0 foundation: **in progress**. M1 read-only rendering: **in progress**. Neither milestone meets its full exit gate.

| Requirement | Implementation | Evidence / remaining gate |
|---|---|---|
| ARC-001/002; M0 | Django/DRF, initial versioned GET contract, generated TypeScript transport types | Parser/API tests and Angular production build pass; no persistent models yet |
| M0 repository/toolchain | Web and Python locks; service configuration; CI; original design kit | Native locks, native builds and Docker startup unverified |
| MD-001/004/007; CONTENT-001/003; ADD-001–006 | Bounded canonical parser, structured tasks, trusted media resolver boundary, opaque revision IDs and title-aware summaries | Original fixture and parser fidelity checks pass; rich native and browser verification remain incomplete |
| MD-002; FEED-002 | Unicode source length, parser nesting/block bounds, excerpt/read time | Source-boundary tests pass; complete per-variant schema limits pending |
| CONTENT-002 | Discriminated nodes, accurate logical spans, structured tasks/authorized image placements, conservative revision identity reconciliation | Task 1/2 contract and parser scopes complete; domain persistence and cross-client rendering still pending |
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


## Task 1 follow-up — strict contract and shared fixtures

Completed the contract scope in `docs/next-10-tasks.md`. JSON Schema now defines exact node variants, leaf/container rules and required heading/link/task/media fields. OpenAPI is synchronized from that source; TypeScript is generated with array-length constraints. Added shared expected canonical documents for all 11 original designer sources and contract rejection tests. The original designer kit is unchanged.

Observed checks in a fresh Python environment installed from the existing lockfile:

- `STMTS_DEVELOPMENT=1 /tmp/stmts-check-env/bin/pytest -q -c stmts/pytest.ini`: **67 passed, 1 xfailed**. The single expected failure narrowly records missing task checkbox state; other fixture changes still fail.
- `npm --prefix stmts/web run generate:api`: **passed**.
- `npm --prefix stmts/web run build`: **passed**.
- `/tmp/stmts-check-env/bin/python stmts/tests/verify_ssr.py`: **passed**, card and reader retain server-rendered fixture content.

The stricter generated model initially exposed empty leaf arrays widening to `unknown[]`. Enabling array-length-aware generation resolved the type error without weakening the schema or casting away renderer types.

Git history now contains a baseline commit, a plan/workflow commit and a cohesive contract implementation commit. No remote is configured and nothing is pushed. The delivered archive preserves the repository metadata and a full Git bundle. M0/M1 remain in progress; task 2 is next. Native/browser/device/database limitations from the initial increment still apply.


## Task 2 and rounded brand review — 8 November 2026

Reviewed the supplied rounded Quote v1.1 package (README, handoff, tokens, license, changelog and preview). Adopted its authoritative monochrome lockups/mark and provided favicons on Angular, while retaining Paper / Forest product styling. Native launcher sources are preserved for future platform work; no native build/mask claim is made.

Accepted architecture addendum 01, ADD-001–006, and completed task 2's parser scope:

- Original source limits precede newline normalization; invalid scalar/NUL input is explicitly rejected. Logical spans cover normalized source lines, including table cells, nested blocks, fences and media promoted out of paragraphs.
- Checked/unchecked/uppercase/nested tasks remain typed nodes with inline formatting intact. The checkbox xfail is removed.
- Fresh opaque IDs use UUID allocation. Trusted previous-tree reconciliation requires matching owner/document scope, aligns unique semantic anchors, preserves stable containers and gives ambiguous duplicate regions fresh IDs. Same-revision fixture regeneration retains IDs.
- Product limits are tested at 49,999/50,000/50,001 code points, 1,999/2,000/2,001 blocks (including table-heavy cases), and depths 11/12/13. Conversion budgets enforce total nodes, inline nesting and cooperative time. Isolated worker memory/wall-time configuration is supplied and tested for success/deadline behavior; deployment integration remains future work.
- A server-trusted resolver and manifest gate media nodes. Missing, foreign, pending, quarantined, wrong-kind and inaccessible assets produce validation feedback; malformed source/manifest identities never become delivery URLs. Repeated placements count distinct manifest assets once. Unreferenced manifest media belongs to the future separate attachment area, not fabricated source blocks.
- Summaries receive title context, retain natural inline spacing, exclude code from reading words and stop excerpts at Unicode grapheme boundaries. Structured failures map to 422 with safe messages and optional line ranges.

Reviewed expectation changes: remove artificial spaces before punctuation in basic/RTL summaries; remove the task plugin's leading marker whitespace; replace four fabricated table-cell [0,0] spans with actual header/body line ranges. No original designer source fixture changed. Expected semantic trees were edited explicitly, not regenerated wholesale from parser output.

Observed validation:

- `STMTS_DEVELOPMENT=1 /tmp/stmts-task2-env/bin/pytest -q -c stmts/pytest.ini`: **143 passed, no xfails**.
- `npm --prefix stmts/web run generate:api`: passed; canonical schema remains the source for generated OpenAPI/TypeScript.
- `npm --prefix stmts/web run build`: passed, production browser/server bundles generated.
- `/tmp/stmts-task2-env/bin/python stmts/tests/verify_ssr.py`: passed for API-backed card and reader HTML.
- Fixture/token/contract regeneration verified stable; contract drift check run after committing generated files.
- Representative single-process measurements (not a load report): 2,000 paragraphs accepted in 85.8ms; 500-row table accepted in 39.4ms; punctuation-heavy safety rejection in 135.4ms; observed peak RSS reached 31,148 KiB across those cases. Hard memory exhaustion stress testing is not claimed.

M0/M1 remain in progress. Task 3 is next: Angular canonical routes, task/media rendering, TOC threshold and failure states. Native builds, browser visual/accessibility/device evidence, persistence, authentication and publishing remain unverified or unimplemented as previously recorded. No remote is configured; commits remain local and included in the source archive/history bundle.
