# ADR 0004: Parser fidelity and revision-local identity

8 November 2026. Adopt architecture addendum 01, ADD-001–006, for task 2. The original source remains unchanged; parsing normalizes only newline representation. Logical line spans are half-open. Canonical task state comes from tokens, never plugin HTML. Opaque IDs are allocated on first parse and reconciled only with a trusted previous tree scoped to the same owner/document.

Reconciliation uses bounded sibling alignment with unique semantic anchors and conservative structural-container matches. Identical duplicate sequences can be retained on unchanged reparse; ambiguous insertions/removals get fresh IDs. This does not infer editor operation history or promise perfect move tracking.

The parser enforces product block/depth/source limits and separate defensive total-node, inline-depth and elapsed-time budgets. A deployment worker boundary provides hard memory/wall-time isolation; it is not falsely claimed to exist in the current in-process fixture endpoint. The adapter exposes structured 422 errors; transport byte caps belong to ingress.

Attachments are resolved only through an injected server-trusted resolver plus a manifest. Read-only tests supply resolvers; no upload/fetch endpoint is introduced. Title-aware summaries derive visible text from the canonical tree and exclude code from reading-time words. Grapheme boundaries are handled with pinned `regex` Unicode \X support.
