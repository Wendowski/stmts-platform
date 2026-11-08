# STMTS — Engineering implementation specification

Version 1.0 · 8 November 2026 · Status: proposed implementation baseline

Audience: AI software engineer and human reviewer. Deliver Angular web, native SwiftUI iOS/iPadOS, native Kotlin/Jetpack Compose Android, and a Python backend.

## 1. Authority and how to use this document

This document turns the designer's initial handoff into a build plan. It defines intended behavior, not an existing implementation or verified production readiness. MUST is required; SHOULD permits a documented justification; MAY is optional.

Read together:

1. This engineering specification for backend behavior, implementation boundaries, and release gates.
2. STMTS_Design_Engineering_Kit_v1.zip, root STMTS_Design_Kit: spec/PRODUCT_SPEC.md for product/interface requirements and original IDs.
3. tokens/design-tokens.json for numerical visual values; DESIGN_GUIDE.md for visual intent.
4. spec/ACCEPTANCE.feature and spec/markdown-fixtures.json for baseline scenarios.
5. concepts/ for screen studies; styles/stmts.css, angular/, native/ and assets/ for integration references.

Keep the original kit read-only under design/reference/. Starter code and contracts.ts are illustrative, not finished applications. Generate definitive models from OpenAPI.

The designer's newer scope governs over the earlier architectural discussion: no quote posts in MVP; Discover is editorial/topic-based; public-only publishing; replies are limited to 5,000 code points. Paper / Forest is the visual baseline. Do not independently select another concept.

For conflicts, preserve the designer's product and visual requirements, record the conflict in docs/decisions/, and resolve before implementing the conflicting behavior. This document's new backend decisions are proposed defaults. Routine implementation choices may proceed; unresolved release-policy decisions in section 16 block the affected release feature.

## 2. Product scope and fixed limits

STMTS supports short statements and long Markdown documents using one Post entity. Public pages are readable without registration.

| Included in MVP | Deferred |
|---|---|
| Accounts, verification, sessions, recovery | Direct messages, private/follower-only posts |
| Following and editorial Discover | Behavioral recommendation training |
| Markdown drafts, preview, publish, edit, delete | Collaborative writing, scheduled publishing |
| Images, limited video, captions/transcript | Live video, arbitrary embeds |
| Replies, likes, bookmarks, plain reposts | Quote reposts, polls |
| Profiles, search, topics, notifications | Federation, advertising, subscriptions |
| Block, mute, reports, moderator tools | Third-party developer platform |

| Field or behavior | Required value |
|---|---|
| Title / summary / original body | 160 / 280 / 50,000 Unicode code points |
| Reply body | 5,000 code points; no title |
| Short-post classification | No title, ≤500 code points, paragraph-only structure |
| Feed excerpt | ≤280 code points with explicit Continue reading |
| Reading time | ceil(non-code plain-text words / 220), minimum 1 minute |
| Parser limits | 2,000 blocks; depth 12 |
| Attachments per post/reply | Up to four images OR one video |
| Image input | JPEG, PNG, WebP, HEIC; ≤20 MiB each |
| Video input | MP4/MOV; ≤250 MiB; ≤180 seconds |
| Alt text / caption | 1,000 / 500 code points |
| Handle | 3–30 ASCII letters/digits/underscore, case-insensitive uniqueness |
| Display name / bio | 80 / 500 code points |

Validate on both clients and server; server is authoritative. Do not silently truncate. Empty text is allowed only with a ready attachment. Feed classification never changes the underlying post type.

## 3. Architecture decisions

| ID | Decision | Implementation consequence |
|---|---|---|
| ARC-001 | Modular Django + Django REST Framework application | Domain modules share PostgreSQL; separate API and worker processes |
| ARC-002 | Versioned REST + OpenAPI | /v1; generated TypeScript, Swift and Kotlin transport models |
| ARC-003 | PostgreSQL is system of record | Constraints enforce uniqueness; Redis is disposable |
| ARC-004 | Celery workers, managed durable broker | Retry-safe tasks; durable outbox for critical side effects |
| ARC-005 | Angular with SSR for public reader/profile | Private routes and personalized payloads excluded from shared caches |
| ARC-006 | SwiftUI and Compose native UI | Native navigation, media pickers, accessibility and secure credential storage |
| ARC-007 | Object storage and CDN with authorization | Quarantine uploads; signed delivery with revocation checks |
| ARC-008 | PostgreSQL full-text search initially | Search abstraction permits later replacement |
| ARC-009 | One region, managed services initially | No multi-region writes or Kubernetes requirement |

Choose mutually supported stable toolchain versions at implementation time, verify official support/security guidance, and commit exact lockfiles plus docs/toolchain.md. This specification does not assert latest version numbers.

Suggested modules: identity, publishing, markdown, media, relationships, feeds, discovery, notifications, moderation, administration. HTTP handlers validate and authorize, domain services implement transactions, selectors implement bounded read queries, and workers handle side effects. Avoid network calls inside database transactions.

## 4. Repository and deliverables

| Path | Contents |
|---|---|
| backend/ | Django project, domain modules, migrations, worker entrypoints |
| web/ | Angular app; feature routes and typed block renderer |
| ios/ | SwiftUI iPhone/iPad app and platform tests |
| android/ | Kotlin Compose phone/tablet app and platform tests |
| contracts/openapi.yaml | Definitive request/response contract |
| contracts/content.schema.json | Versioned discriminated block-tree schema |
| contracts/fixtures/ | Shared source, canonical trees and rendering expectations |
| design/reference/ | Unmodified extracted designer kit |
| design/generated/ | Generated CSS, Swift and Kotlin semantic tokens |
| infra/ | Reproducible environment configuration and deployment definitions |
| docs/decisions/ | Architecture and product decision records |
| docs/runbooks/ | Restore, rollback, abuse response, media failure procedures |
| tests/acceptance/ | Requirement-linked cross-client scenarios |

Supply documented local startup, seeded development accounts, sample posts, test media, .env.example without secrets, and CI commands. Production builds MUST fail or exclude development authentication and fixtures.

## 5. Data model and invariants

Use opaque UUID identifiers and UTC timestamps. Keep internal fields out of public serializers.

| Entity | Key fields / constraints |
|---|---|
| Account/Profile | Immutable user ID, normalized unique email/handle, display name, bio, account status |
| HandleAlias | Reserved former handle → immutable account ID; no unsafe reassignment |
| Draft | Owner, source/title/summary, attachment manifest, revision, basePostId/basePostRevision for edits |
| Post | Author, public ID, replyTo/root IDs, publishedAt, currentRevision, status |
| PostRevision | Unique post+revision; source, dialect, canonical tree, derived text/excerpt, media manifest, timestamps |
| MediaAsset | Owner, immutable object identity, checksum, type/state, variants, alt/decorative/caption, accessibility metadata |
| PostMedia | Post revision + media association and position; enforce ownership and count/type limits |
| Follow/Like/Repost/Bookmark | Unique actor+target; bookmark private |
| Block/Mute | Unique actor+target; no self-relations |
| Topic/PostTopic | Editorial topic taxonomy and approved assignment |
| Notification | Recipient, actor, event/target IDs, readAt, deduplication key |
| Report/ModerationAction | Reporter, target, reason, status, staff action/audit metadata |
| IdempotencyRecord | Unique actor+operation+key; request fingerprint, outcome/resource ID |
| OutboxEvent | Unique event ID, payload reference, delivery status and attempt count |
| Session/Device | Session revocation state; push token scoped to current account |

DB-001 Enforce relationships with database uniqueness and foreign keys, not preflight checks alone. Index post author+publishedAt+ID, reply parent+publishedAt+ID, and relationship lookups in both directions. Index search vectors; prove query behavior with representative data.

DB-002 Publication creates Post, revision, associations, idempotency outcome and outbox event in one transaction. Consumers deduplicate by event ID. Broker outages do not lose committed notifications/index updates; an outbox sweeper resumes delivery.

DB-003 Public edits preserve ID/publishedAt and require matching post revision. Deletion makes the body unavailable synchronously, invalidates delivery access, and queues derived-content cleanup. Reply ancestry may retain an empty tombstone. Retained revisions are staff-only until a public revision-history policy exists.

DB-004 Counters are derived or transactionally maintained and repairable from relationships. Concurrent toggles cannot create duplicate rows or negative counts. Self-follow/like policy defaults: self-follow forbidden; self-like forbidden.

## 6. Identity and authorization

AUTH-001 First-party accounts use verified email and password, secure password hashing, single-use expiring verification/recovery tokens stored hashed, generic recovery responses and rate limits. Social login is optional later.

AUTH-002 Web uses same-origin secure HttpOnly session cookies and CSRF protection. Native uses OAuth authorization-code flow with PKCE through the system browser, a maintained authorization-server integration, short-lived access tokens and rotating revocable refresh credentials. Do not invent an OAuth protocol or store web bearer tokens in localStorage.

AUTH-003 Store native credentials in Keychain/Keystore-backed storage. Revoke sessions on password reset and device sign-out; remove push registration/account caches on sign-out. Browser IndexedDB draft storage is account-scoped and is not claimed to be encrypted against a compromised browser.

AUTH-004 Every mutation checks actor, account status, object ownership and relationship policy. Drafts, bookmarks, session records and reports are never anonymously readable. Moderators use separate permissions and audited staff access.

AUTH-005 Public means anonymously accessible: a block is not confidentiality. A block in either direction prevents authenticated interaction and filters the affected accounts from authenticated feeds, search and conversation views. Mute affects only the muter's discovery/feeds/notifications, not direct public URLs. Document this behavior in product copy.

## 7. API contract

All JSON uses camelCase, opaque string IDs, ISO 8601 UTC timestamps, and nullable fields defined explicitly in OpenAPI. Lists default to 20, maximum 50. Cursors are opaque and tamper-resistant. Stable tie-breaking is mandatory.

| Operation | Contract / key behavior |
|---|---|
| POST /v1/auth/register, /verify, /recover, /reset | Enumeration-safe identity flows; limits and token expiry specified in config |
| GET /v1/me; GET /v1/sessions; DELETE /v1/sessions/:id | Current account and session revocation |
| GET/PATCH /v1/me/profile | Profile and optimistic concurrency |
| GET /v1/users/:id; GET /v1/handles/:handle | Public profile/handle resolution |
| PUT /v1/users/:id/follow, /mute, /block | {active:boolean}; canonical state |
| GET /v1/feed?mode=following|discover&topic=&cursor= | Page of feed entries |
| GET /v1/users/:id/posts?cursor= | Public profile timeline |
| GET /v1/posts/:id; GET /v1/posts/:id/replies?cursor= | Current visible revision; neutral unavailable response |
| POST/GET /v1/drafts; GET/PATCH/DELETE /v1/drafts/:id | Private revisioned draft storage |
| POST /v1/preview | Draft ID/revision → canonical tree, validation, previewHash |
| POST /v1/posts | draftId, revision, previewHash plus Idempotency-Key |
| PATCH /v1/posts/:id | Publish edit from edit draft; If-Match, previewHash and idempotency key |
| DELETE /v1/posts/:id | Owner delete; confirmed client intent; repeat-safe |
| PUT /v1/posts/:id/like, /bookmark, /repost | {active:boolean}; counts and canonical viewer state |
| GET /v1/bookmarks?cursor= | Private saved posts |
| POST /v1/uploads | Metadata → bounded upload session/authorized destination |
| POST /v1/uploads/:id/complete | Confirm uploaded bytes; async processing |
| GET/DELETE /v1/uploads/:id | Status or cancellation |
| POST /v1/media/:id/import | Explicit external image import; owner-only SSRF-safe fetch |
| GET /v1/search?q=&type=posts|people|tags&cursor= | Permission-filtered results |
| GET /v1/topics | Editorial topics |
| GET /v1/notifications; PUT /v1/notifications/:id/read | Private notifications |
| POST /v1/notifications/read-all | Explicit read-through timestamp |
| PUT/DELETE /v1/devices/:id | Account-scoped push registration |
| POST /v1/reports | Idempotent target/reason/details submission |
| GET/PATCH /v1/me/settings | Theme, data saver, notification preferences |
| POST /v1/me/exports; GET /v1/me/exports/:id | Authenticated export job and expiring download |
| DELETE /v1/me | Reauthenticated deletion request |

Replies publish through drafts carrying replyTo; server derives root and prevents ancestry changes/cycles. Reposts use separate feed-entry IDs with kind, actor, originalPost and occurrence timestamp. Deduplicate pagination by entry ID; cache original post state by post ID. This extends the kit's illustrative Page<PostSummary> to preserve repost attribution.

API-ENG-001 PATCH draft uses integer revision and If-Match. Mismatch returns 409 with current revision; clients retain both sources. ETag is also returned on reads. Published edit conflicts follow the same rule.

API-ENG-002 Preview hash binds owner, draft/revision, dialect/parser version, attachment IDs/versions, metadata and canonical content hash. Publication revalidates all eligibility and ownership; preview is not an authorization token.

API-ENG-003 Publication returns 201 and canonical post; a retry of the same key/fingerprint returns the original successful outcome. A different payload with the same key returns 409 IDEMPOTENCY_MISMATCH. Persist client keys until outcome is known. Keep durable draft→publication identity and edit operation IDs so late retries cannot duplicate content after key cleanup.

API-ENG-004 Errors use {code,message,fieldErrors?,requestId,retryAfter?}. Statuses: 401 unauthenticated, 403 forbidden, neutral 404 unavailable, 409 conflict, 413 too large, 422 invalid, 429 rate-limited, 5xx retryable service failure. Include Retry-After for 429. Never expose source, credentials or stack traces in errors.

## 8. Markdown and publication algorithm

CONTENT-001 Implement stmts-md/1: CommonMark 0.31.2 plus tables, strikethrough and read-only task lists. No raw HTML, arbitrary SVG, scripts, iframes, math, executable diagrams or arbitrary embeds. Disallowed HTML is escaped literal text.

CONTENT-002 Produce a discriminated canonical tree with block IDs, type, children/text, source spans, heading depth, safe link destinations or attachment IDs. Publish a JSON Schema with explicit node variants, maximum depth and no arbitrary properties. Include paragraphs, text/marks, headings, links, lists/items, quotes, rules, code, tables/cells, tasks and media nodes. Stable IDs survive unchanged blocks across edits; allocate new IDs for new blocks. Hash document identity with IDs where appropriate.

CONTENT-003 Render through typed platform components, escaped text and validated URLs. No Angular trust bypass or native unrestricted HTML WebView. Body headings map to display levels 2–6; page has one h1. TOC appears at three headings and uses stable block anchors.

CONTENT-004 Only http, https and mailto links. Media source uses stmts-media:UUID with owner/association validation. External image syntax stays literal until explicit import succeeds. Import worker denies private/link-local/metadata destinations, rechecks DNS/redirect hops, bounds bytes/time and permits only approved image formats.

Publication sequence:

1. Authenticate, apply rate limit and locate/reserve idempotency operation.
2. Lock draft, check revision and edit target ownership/revision if applicable.
3. Validate text limits, attachment readiness/ownership/type limits, accessibility metadata and current moderation eligibility.
4. Verify preview binding; parse/derive again if necessary. Reject stale inputs with recoverable field feedback.
5. Atomically write post/revision, media associations, operation outcome and outbox event.
6. Commit before dispatch. Return canonical post. Clients clear local draft only on confirmed success.
7. Workers deliver notifications and derived search updates with retries/deduplication.

Do not queue offline publication. Saving locally and later publishing are separate explicit actions.

## 9. Draft and media durability

DRAFT-001 Local snapshot after 500ms inactivity; remote save after 1,000ms. Serialize remote saves per draft and ignore stale responses. Display Unsaved, Saving, Saved remotely, Saved on this device and Conflict accurately.

DRAFT-002 Keep title/source/media/selection across navigation, rotation and preview. Preserve local and remote copies on 409; offer compare, duplicate and confirmed reload. Account switch cannot surface another user's drafts. Warn before discarding unsynced work.

MEDIA-ENG-001 Upload sessions have owner, expiry, byte limit, checksum and unique object key. Validate bytes independently of client MIME. Image decoding enforces pixel/decompression bounds. Strip GPS/EXIF; normalize orientation; generate responsive derivatives.

MEDIA-ENG-002 Server states: awaitingUpload → processing → ready; terminal failed/quarantined/cancelled. Client additionally tracks selected/validating/uploading/progress. Completion is idempotent. Expired sessions restart without duplicate published associations. Sandbox workers and use maintained decoders.

MEDIA-ENG-003 Video delivery includes poster, adaptive variants and H.264/AAC MP4 fallback. Require WebVTT captions or transcript for meaningful audio, or explicit no-meaningful-audio declaration. Label transcript-only content accurately; do not claim synchronized captions.

MEDIA-ENG-004 Originals/quarantine remain private. Delivery checks current asset publication status; copied links must stop working after deletion/quarantine, including at the CDN. Signed URL expiry alone is insufficient for immediate revocation: use an edge deny/revocation check or equivalent invalidation strategy verified in tests. Content already downloaded cannot be remotely erased.

MEDIA-ENG-005 Schedule orphan/session cleanup, bounded processing retries, dead-letter handling and operator replay. Retain source draft on failure. Never autoplay video or fetch full videos in feed.

## 10. Feeds, discovery, search and notifications

FEED-ENG-001 Following includes eligible posts/replies policy below and repost events from followed accounts. Default feed shows original top-level posts and reposts; replies remain in conversations/profile replies. Include the user's own top-level posts. Cursor orders by immutable occurrence timestamp and entry ID descending with a fixed initial upper bound. New statements appear behind an explicit refresh action.

FEED-ENG-002 Begin with indexed relational queries and bounded page sizes. Do not build fan-out infrastructure before measurements justify it. Filter account/deletion/block/mute states at read time even if candidates are cached.

DISC-001 Discover uses staff-managed topic assignment and chronological publication order. Search uses PostgreSQL text search over public eligible revisions and normalized account/tag fields. MVP hashtag linking derives tags from plain text, never code. Do not imply personalized or semantic ranking.

NOTIFY-001 Outbox consumers create deduplicated in-app events for replies, mentions, follows, likes and reposts, excluding self-actions and forbidden relationships. Push is opt-in, contains minimal text, and deep links recheck current access. Poll in-app notifications with backoff initially; realtime infrastructure is optional.

## 11. Design and client implementation rules

| Concern | Required baseline |
|---|---|
| Visual identity | Paper / Forest; use supplied wordmark/icons and semantic tokens |
| Themes | Separate light/dark token pairs; System/Light/Dark; apply before first paint |
| Reading | Serif 20px/1.7 baseline, ≤68ch; native scalable equivalents |
| Compact | <768 CSS px; 16px gutters; bottom navigation |
| Medium | 768–1199; 80px navigation rail |
| Expanded | ≥1200; shell ≤1280, nav216, feed≤680, optional rail272, gaps24 |
| Touch targets | Web/iOS ≥44 units; Android ≥48dp |
| Accessibility | WCAG 2.2 AA target; VoiceOver/TalkBack; reduced motion; RTL |

Generate tokens rather than maintaining three independent palettes. Reuse shipped CSS deliberately; do not turn static HTML demos into application architecture. Native uses logical dimensions and scalable text, not physical-pixel copies.

Implement all routes in the designer's information architecture. Every route defines loading, ready, empty, error, offline/stale and unavailable states as applicable. Auth-required actions retain return location but never automatically publish after sign-in. Back restores feed anchor and focus.

Angular SSR public responses contain no viewer-specific likes/bookmarks/session data. Fetch viewer state privately after hydration. Use request-scoped server services; never reuse user state across SSR requests. Native universal/app links use canonical IDs; slugs are cosmetic.

## 12. Operations, security and privacy

OPS-001 Separate development, staging and production identities/data/secrets. Use infrastructure as code, TLS, least-privilege service roles, secret management, immutable releases and migration rollback/forward-fix procedures.

OPS-002 Log request/event IDs, timings and sanitized error codes. Never log passwords, tokens, private draft bodies or complete upload URLs. Measure API latency/error rate, queue lag, failed uploads, publish retries, outbox backlog, media delivery cost and moderation backlog.

OPS-003 Proposed launch objectives: 99.9% monthly core-read/API availability; p95 read API ≤400ms excluding transfer, publish ≤1s excluding upload; web p75 LCP≤2.5s, INP≤200ms, CLS≤0.1. These are targets, not tested results. Initial benchmark: 100 concurrent readers, 10 publish requests/second, 100,000 seeded posts and 10,000 accounts; record dataset, hardware and actual outcomes.

OPS-004 Proposed recovery objectives: RPO≤15 minutes, RTO≤4 hours with point-in-time database recovery and object protection. Demonstrate restore and reconciliation in staging before claiming compliance. Cost estimates require measured media/storage/egress usage.

SEC-001 Threat-model XSS, SSRF, object-level authorization, malicious decoders, credential abuse, bot spam, cache leakage and webhook forgery. Apply CSP, CSRF controls, strict allowed origins, rate limits and payload/time bounds. Verify signed vendor webhooks and deduplicate.

SEC-002 Moderation console supports report triage, content quarantine, account restriction, reasoned actions and immutable staff audit events. Report, block and mute must function before admitting external beta users.

PRIV-001 Export includes the requester's posts/source/media and account data, not other users' private records. Reauthenticate deletion, revoke sessions immediately and remove public access while deletion jobs run. Define audit/backups/legal-retention exceptions and explain them accurately before release.

## 13. Verification and acceptance matrix

| Test ID | Requirement coverage | Required evidence |
|---|---|---|
| T-01 | MD-001–007; CONTENT-001–004 | Shared fixtures parse/render across clients; hostile links/HTML never execute or fetch |
| T-02 | WRITE-001–005; DRAFT-001–002 | Network loss, two-device conflict, account switch, preserved source |
| T-03 | API-ENG-001–003; DB-002 | Concurrent publishes, lost response, same-key mismatch, late retry → one post |
| T-04 | MEDIA-001–005; MEDIA-ENG-001–005 | Wrong MIME, oversized decoded image, corrupt video, expired upload, quarantine |
| T-05 | AUTH-003–005; SOC-002 | Cross-account draft access denied; blocked writes/search/cache behavior verified |
| T-06 | READ-002; DB-003 | Stale edit rejected; delete removes search/body/media; reply tombstone preserved |
| T-07 | FEED-001–003; SOC-001 | Same-time cursor boundaries, repost identity, refresh, rapid toggles and rollback |
| T-08 | A11Y-001–004; UI-001–002 | Keyboard, screen readers, RTL, large text, both themes and narrow windows |
| T-09 | PERF-001–002; OPS-003 | Representative load report, web metrics, native sustained scrolling |
| T-10 | OPS-004; DB-002 | Broker outage replay, duplicate events, backup restore, failed deploy recovery |
| T-11 | AUX-001–004 | Search cancellation, deleted notifications, handle redirects, preference persistence |
| T-12 | AUTH-001–002; PRIV-001 | Recovery token replay denied, session rotation/revocation, export/deletion isolation |

Import every original ACCEPTANCE.feature scenario and extend it; passing new tests does not replace original acceptance. Use actual PostgreSQL for concurrency/constraint tests, not SQLite. OpenAPI validation and generated-client drift checks run in CI.

Web matrix: 320/390/834/1440 CSS widths, 200% text, 400% browser zoom. Native: iPhone, iPad split view, Android phone/tablet, largest text, real-device image/video playback and deep links. Automated checks supplement manual accessibility verification.

## 14. Implementation milestones

Each milestone is a small set of reviewable changes. Complete its acceptance checks before continuing to dependent work.

| Milestone | Deliverables | Exit condition |
|---|---|---|
| M0 Foundation | Repository, toolchain, local services, CI, reference kit and decision log | All projects compile; startup documented |
| M1 Contract and rendering | OpenAPI, block schema, parser, tokens, PostCard/Reader in all clients | Same fixture renders in both themes; T-01 and initial T-08 pass |
| M2 Public reading and identity | Real DB/API reader/profile, SSR, sign-in/recovery, native auth/deep links | Public URL works signed out; private data isolated |
| M3 Text publishing | Local/remote drafts, conflict UI, preview, idempotent publish, edit/delete | T-02/T-03 and text portion of T-06 pass end to end |
| M4 Social and discovery | Follows, feed, replies, reactions, search, saved, notifications | T-05/T-07/T-11 pass; real data replaces fixtures |
| M5 Media | Image/video pipelines, accessible metadata, retries, revocation | T-04 and media portions of T-06 pass on devices |
| M6 External beta readiness | Reports, moderation, privacy flows, operational controls | Security/accessibility review and restore drill complete |
| M7 Release candidate | Full original acceptance suite, load report, device evidence | No unresolved critical/high security issues; policy gates closed |

No milestone may be called complete solely because screenshots exist. A local fixture-backed UI must be labeled as such. A production-ready claim requires observed integrated evidence.

## 15. Instructions for the AI software engineer

Before coding: read repository AGENTS.md, this document, designer PRODUCT_SPEC.md, BUILD_ORDER.md, tokens, and acceptance fixtures. Inventory the repository; extend existing conventions. Do not regenerate working apps unnecessarily.

For each task:

1. State requirement IDs and the smallest end-to-end behavior to implement.
2. Define/update contract and migration before consumers when needed.
3. Implement authorization and failure behavior with the happy path.
4. Add meaningful boundary/concurrency/security tests; run affected checks.
5. Record changed files, exact commands/results, screenshots or device evidence where relevant, deviations, and remaining blockers.
6. Update docs/implementation-status.md with requirement→implementation→test mappings. Distinguish implemented, tested, blocked and deferred.

Do not add deferred features, replace native apps with wrappers, invent endpoints outside the contract, bypass rendering safety, log draft content, or hide failing checks. Use development fixtures only in explicitly named development/test modes.

Suggested initial task:

> Implement M0 and the M1 read-only slice for STMTS using this specification and the unmodified designer kit. Establish the Python API contract and canonical Markdown fixture, generate semantic tokens, and implement PostCard and Reader in Angular, SwiftUI and Compose. Demonstrate compact/expanded layouts, both themes, loading/unavailable states, and large text. Do not implement publication yet. Return changed files, requirement coverage, actual build/test results, and unresolved decisions.

## 16. Decisions to close before public release

Engineering may proceed with the proposed architecture. The following need named owners and recorded decisions rather than fabricated policy:

| Decision | Proposed working assumption | Gate |
|---|---|---|
| Deployment region/provider and public domain | One region; configurable example origins locally | Production infrastructure/deep links |
| Age eligibility, terms, privacy and jurisdiction | Invite-only development; no claim of legal approval | External beta registration |
| Retention/deletion/backup exceptions | Immediate public removal; configurable cleanup jobs | External beta |
| Moderation staffing and appeals | Staff queue and audited actions | External beta |
| Email, OAuth server, video/scanning vendors | Adapter interfaces; local test implementations | Real delivery and media release |
| Signup/media quotas and budget | Configurable bounded limits; conservative invite caps | External beta |
| App-store identities and signing | Development builds until credentials are supplied | Store distribution |
| External-image import readiness | Keep external images literal if secure importer is incomplete | Do not expose import action before completion |

## 17. Source notes

Primary product inputs reviewed: STMTS_Product_Spec.md; STMTS_Design_Guide.pdf; and extracted STMTS_Design_Engineering_Kit_v1.zip including contracts.ts, ACCEPTANCE.feature, BUILD_ORDER.md and design-tokens.json. Architectural additions here are proposed STMTS decisions.

Official implementation references checked 8 November 2026:

- Angular security: https://angular.dev/best-practices/security — framework rendering safety.
- Angular SSR: https://angular.dev/best-practices/performance/ssr — public-page rendering options.
- Django transactions: https://docs.djangoproject.com/en/4.2/topics/db/transactions/ — transaction semantics reference; use the selected release's matching documentation during implementation.

These references inform framework behavior; they do not validate STMTS's unbuilt implementation.
