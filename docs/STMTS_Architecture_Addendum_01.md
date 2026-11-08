# STMTS architecture addendum 01

Parser fidelity, content identity and the next engineering handoff

Version 1.0 · 8 November 2026 · Proposed implementation direction

## Purpose and reviewed baseline

This addendum supplements STMTS_Engineering_Spec_v1.md. It resolves implementation details for task 2 in docs/next-10-tasks.md of STMTS_Source_v0.1.0.zip, reviewed at Library version 1. It does not change product scope or mark any software milestone complete.

Reviewed: AGENTS.md, README.md, docs/implementation-status.md, docs/next-10-tasks.md and backend/content/parser.py. Reported previous validation is 67 passing tests and one expected failure, successful Angular generation/build and SSR checks. Those results are the engineer's recorded evidence; they were not rerun for this architecture review.

The source states M0/M1 remain incomplete. Native rendering/builds, browser accessibility verification and persistent database functionality remain pending. Preserve existing Git history and commit each cohesive implementation with its tests and status updates.

## 1. Immediate work order

Continue task 2: parser fidelity, task lists, spans, limits and stable IDs. Do not advance to authentication, persistent publication or media uploads until their prerequisite rendering gates are satisfied.

The initial parser may be refactored into smaller modules while preserving its consumers through an adapter. Suggested responsibilities: dialect configuration, parsing/normalization, validation, identity reconciliation and summary derivation. Avoid an unnecessary parser replacement if the existing dependency can meet the contract.

New decisions in this addendum use identifiers ADD-001 onward and should be recorded in docs/decisions/ before implementing dependent behavior.

## 2. Canonical source and span rules

ADD-001 Store the original submitted Unicode source unchanged. Derive a parsing view with CRLF and lone CR normalized to LF. Code-point limits apply to submitted source before newline normalization. Reject invalid Unicode scalar input explicitly; never normalize Unicode composition or replace characters silently.

For the existing sourceSpan pair, use zero-based logical line positions [startLine,endLine), end exclusive, in the LF-normalized view. Document this in JSON Schema and OpenAPI. A sourceSpan is not a byte offset or a browser selection range.

Every source-backed block requires an accurate span. Inline nodes may omit spans while the contract remains line-based. Synthetic containers use the bounding span of their source-backed descendants. Do not use [0,0] as an unknown-span placeholder. If a node variant permits absent spans, omit rather than fabricate them.

Example: source "alpha\n\nbeta" yields paragraph spans [0,1] and [2,3]. A trailing newline does not create an extra paragraph. Fenced code spans include opening and closing fence lines where present.

If exact character selection is added later, introduce explicit normalized-code-point offsets and source mapping as a versioned extension. JavaScript uses UTF-16 indices; Swift commonly exposes grapheme-oriented operations. Clients MUST convert deliberately rather than assuming these equal Python code-point offsets.

Acceptance:

- LF/CRLF/CR fixtures have identical semantic trees and logical spans.
- Blank lines, nested lists/quotes, tables and unclosed fences have accurate boundaries.
- Emoji, combining marks, CJK and bidi text remain unchanged in source/text.
- No unknown span is emitted as a fabricated zero-length range.

## 3. Read-only task lists

ADD-002 Task checkbox state belongs to the canonical task node, not generated HTML. Preserve checked versus unchecked state and the existing schema's exact node names. Both [x] and [X] mean checked; [ ] means unchecked. Marker syntax is recognized only in a list-item position allowed by the selected task-list extension.

The current task-list plugin creates HTML tokens and parser.py discards html_inline tokens. Replace that loss of meaning with token metadata or a controlled plugin adapter. Do not consume arbitrary plugin HTML as application markup or introduce an HTML trust bypass.

The adapter must preserve inline formatting, links and nested children following the checkbox marker. Ordinary bracket text, fenced code and escaped markers remain literal. Tasks render read-only with an accessible checked/unchecked announcement; they are not editable controls in the public reader.

Acceptance:

- Checked, unchecked, uppercase X, nested tasks and mixed task/ordinary lists.
- Emphasis and safe links within a task retain structure.
- A task marker inside code does not create a task.
- The existing expected-failure test becomes a normal passing assertion.
- Original designer fixtures remain unchanged; derived expected trees may change only with documented semantic justification.

## 4. Stable block IDs across revisions

ADD-003 Block IDs are document-local opaque identity, not content hashes. Identity reconciliation accepts the previous canonical tree for the same document. Never accept a previous tree belonging to another account/document as an authoritative source.

Current content-hash-plus-occurrence IDs are insufficient: inserting identical earlier content can renumber existing blocks, and parent fingerprints can inherit descendant/span changes.

Required algorithm properties:

1. Parse a new tree without trusting caller-supplied IDs.
2. Compute semantic fingerprints from type, content attributes and descendant semantics; exclude IDs, spans and runtime fields.
3. Match unchanged blocks using order-preserving sibling alignment and surrounding unique anchors.
4. Preserve prior IDs for confident matches, including nodes whose source line moved.
5. Give new or ambiguous blocks fresh IDs; never reuse one old ID for two nodes.
6. Reconcile descendants within matched containers. Preserve a container's ID when only children are edited if its structural position and type are confidently matched.

Duplicate blocks are intrinsically ambiguous without editor operation history. Do not promise perfect identity inference. When insertion or deletion makes matching ambiguous, prefer fresh IDs for the ambiguous region and preserve unambiguous surrounding IDs. Deterministic matching and no incorrect identity reuse matter more than keeping every ID.

For first parse, generate fresh opaque IDs. Tests must compare semantic shape separately from identity; fixtures requiring deterministic IDs may use an injected test allocator. Do not put a production fixed seed into ID generation.

Acceptance:

- Inserting a paragraph before an unchanged unique heading preserves that heading's anchor.
- Moving source lines does not alter unchanged semantic fingerprints.
- Duplicate insertion/removal keeps IDs unique and never maps one old node twice.
- Editing a list child does not unnecessarily replace unrelated sibling IDs.
- Repeated preview of an unchanged revision reuses its persisted canonical tree or previous IDs.
- Reconciliation is bounded for pathological repeated content; avoid unbounded quadratic matching.

## 5. Parser budgets and failure semantics

ADD-004 Product limits remain 50,000 source code points, 2,000 blocks and nesting depth 12. Replies additionally require the 5,000-code-point limit at the publication boundary.

Define block count as every canonical block-level node, including list items and table rows/cells/containers. Text and inline-mark nodes do not count toward the block limit. Define depth as nested block containers: document is depth 0; top-level blocks depth 1. Inline formatting nesting has a separate implementation safety limit, not an accidental product block-depth rule.

Count during conversion, before constructing a large canonical tree. Validate nesting before a parser's internal maxNesting silently flattens or truncates content. Deep unsupported input must produce a clear limit error, not an apparently successful partial document.

Add configurable defensive budgets for total canonical nodes, processing time and worker/request memory. Proposed initial total-node safety cap: 20,000 including inline nodes; document it as a defensive implementation cap and return CONTENT_COMPLEXITY_LIMIT when exceeded. Benchmark before revising it. Do not claim all 50,000-character inputs are always acceptable regardless of structure.

Parser failures expose structured code, safe message and line span when available. Do not include full user source in logs. The HTTP adapter maps product/complexity violations to 422; transport byte-size violations remain 413.

Test exact boundaries at 49,999/50,000/50,001 code points, 1,999/2,000/2,001 blocks and depths 11/12/13. Include table-heavy, deeply nested and punctuation-heavy payloads. Verify complete rejection rather than truncation.

## 6. Attachment resolution without inventing a media service

ADD-005 Give parsing an explicit attachment-resolution boundary. A trusted resolver supplied by the server returns attachment identity, ownership/association eligibility, kind, readiness and accessibility metadata. A source UUID alone never grants access.

For this read-only increment, use a test resolver for positive and negative cases. Do not create fake production upload endpoints, ready flags controlled by the client or unrestricted network fetching.

For stmts-media:UUID images:

- A valid authorized image becomes the existing canonical media variant with an attachment ID.
- Missing, foreign, wrong-kind, pending or quarantined assets produce explicit validation feedback.
- Preview may show a safe Missing media placeholder; publication must reject unresolved media.
- Four image references to the same attachment count as one uploaded asset but may have multiple placements. Product attachment-count limits count distinct manifest assets.
- The server compares all inline references with the attachment manifest; unattached manifest images may render once in the attachment area.

External image URLs remain literal source/text with feedback; no image request occurs. Unsupported SVG/data URLs must not become media. Video remains a structured manifest attachment, not HTML or an improvised Markdown extension.

Tests assert that unauthorized cases never expose object URLs. Use a resolver that records calls to prove malformed schemes are rejected before resolution.

## 7. Derived text and preview parity

ADD-006 Derive visible text from the canonical tree, never by stripping raw Markdown with regular expressions. Code/codeInline is excluded from reading-time words; headings, task text, list text and table text contribute. Task checkbox markers do not count as words.

Preserve designer FEED-002: short means titleless, at most 500 code points and paragraph-only. The current parse(source) entry point lacks title context. Keep source analysis separate from a post-summary service that receives title and computes final isShort; a titled short body must not be classified as a short post.

Excerpt uses at most 280 code points; avoid splitting a combining/emoji sequence by stopping earlier at a grapheme boundary when necessary. Plain-text fixtures must specify expected spacing around adjacent inline marks and links.

The 220-words/minute rule is an approximate product rule, not a language-independent estimate. Retain it for MVP and label reading time approximately; localized segmentation can be a later versioned change.

## 8. Contract changes and compatibility

Use contracts/content.schema.json as the canonical node-shape source. Regenerate OpenAPI and TypeScript through existing scripts. Native generation follows in tasks 4/5. Do not hand-edit generated types to suppress errors.

Field clarifications that do not change shapes can remain schema version 1.0 with documented semantic notes. Any incompatible shape change requires an explicit schema-version decision, updated fixtures and client compatibility handling. Preserve dialect stmts-md/1 unless writing syntax semantics change.

Add a semantic-tree fixture comparator that excludes opaque IDs while independently testing ID uniqueness and reconciliation. Golden fixtures must be reviewed expectations, not regenerated outputs accepted automatically.

## 9. Required completion evidence

Task 2 is complete only when:

- All original source fixtures and strict contract rejection tests pass.
- Task-checkbox expected failure is removed because behavior passes.
- Source spans, resource boundaries, title-aware summary and duplicate identity tests pass.
- Generated contract/type drift checks and Angular production build pass.
- SSR reader/card checks still pass.
- docs/implementation-status.md and docs/next-10-tasks.md identify actual coverage and remaining native/browser gates.
- Cohesive changes have descriptive commits and a clean working tree.

Native builds and browser accessibility must remain labeled unverified until run. This addendum does not require claiming those unrelated checks have passed to finish parser task 2.

## 10. Next tasks after parser acceptance

| Order | Engineer deliverable | Dependency |
|---|---|---|
| 3 | Angular canonical /p/:id route, task/media nodes, TOC threshold and failure states | Accepted parser and generated contracts |
| 4 | SwiftUI rich rendering and generated transport types | Shared expected semantic fixtures |
| 5 | Compose rich rendering and generated transport types | Same shared fixtures |
| 6 | Locked native builds and Apple/Android CI | Native implementations |
| 7 | Visual/accessibility evidence and fixes | Working clients and actual devices/browser |
| 8–10 | PostgreSQL models, persistent public reading, verified identity | M0/M1 exit gates satisfied |

## AI engineer execution prompt

> Continue task 2 in the existing STMTS Git repository. Read AGENTS.md, the original engineering/product specs and STMTS_Architecture_Addendum_01.md. Preserve history and design/reference. Implement task state, accurate logical-line spans, bounded parser conversion, previous-tree ID reconciliation, a testable attachment resolver and title-aware post summaries. Use the existing strict schema as authority; regenerate dependent contracts/types. Remove the task-state xfail only after it passes. Run parser/contract tests, drift checks, Angular build and SSR checks. Commit coherent changes with tests and status notes. Return actual commit IDs, check results and remaining gates. Do not implement publishing or fake production media services.
