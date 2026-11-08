# Next 10 engineering tasks

Ordered from the architect's M0/M1 dependencies toward M2. Each task is a reviewable change with its own commit; no public release is implied.

| # | Task | Exit condition | Status |
|---|---|---|---|
| 1 | Strict content-node variants and shared expected-output fixtures | JSON Schema rejects invalid shapes; OpenAPI and generated TypeScript stay synchronized; fixture expectations expose known parser gaps | In progress |
| 2 | Parser fidelity: task lists, spans, limits and stable IDs | Checked/unchecked state preserved; authorized media references defined; duplicate edits and parser boundaries tested | Pending |
| 3 | Angular rendering and canonical reader routes | Rich node variants rendered safely; `/p/:id` works signed out; loading/unavailable states and TOC verified | Pending |
| 4 | SwiftUI rich renderer and generated transport models | Same canonical fixtures retain inline formatting, lists, tables and safe links | Pending |
| 5 | Compose rich renderer and generated transport models | Same canonical fixtures retain inline formatting, lists, tables and safe links | Pending |
| 6 | Reproducible native builds and CI | Locked native dependencies, checked-in Android wrapper and successful Apple/Android builds | Pending |
| 7 | Responsive, theme and accessibility verification | Required widths, zoom, keyboard, RTL and device assistive-technology evidence; issues fixed | Pending |
| 8 | PostgreSQL account/publication models and migrations | DB constraints and indexes tested on PostgreSQL; fixture endpoint remains development-only | Pending |
| 9 | Persistent public reading, profiles and pagination | Real public data, permission-aware reads and stable cursors replace fixture reads | Pending |
| 10 | Verified accounts and secure sessions | Verification/recovery, CSRF-protected web sessions and maintained native PKCE integration verified | Pending |

M0/M1 must meet their full release gates before dependent feature work. Tasks 8–10 do not authorize skipping unfinished rendering/build/accessibility work.

## Commit convention

Commit each coherent implementation with its relevant tests and documentation. Use an imperative message with a scope where helpful. Keep generated contracts in the same commit as their source change. Before a handoff, check that the working tree is clean and report actual checks and remaining gaps. Do not rewrite completed history without explicit instruction.

Repository branch: `main`. No remote is configured; commits are local and preserved in the delivered Git bundle until a remote is provided.
