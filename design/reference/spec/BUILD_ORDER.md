# Build order for an AI software engineer

Read README.md, DESIGN_GUIDE.md, PRODUCT_SPEC.md, then tokens/design-tokens.json. Treat the selected Paper / Forest direction as the visual baseline. Do not choose an alternate concept without a product decision. Do not invent production endpoints or report completion from screenshots alone.

1. Scaffold platform projects in the actual application repository. Select supported framework/toolchain versions at implementation time; lock dependencies. Configure lint, format, typed API generation and platform CI. Keep this kit as read-only design input.
2. Generate web/native semantic tokens from JSON. Implement typography, buttons, inputs, icons, tabs, banners, dialog/sheet and post-card primitives. Verify both themes and large text before feature work.
3. Define OpenAPI and canonical Markdown block schema with the Python service. Implement parser limits, media references, safe URLs, authorization and shared fixtures first. Treat contracts.ts as illustrative shape, not a complete schema.
4. Build public reader and profile with loading/unavailable/error states. Implement SSR/share metadata on Angular and deep-link resolution on native. Verify one article across all clients.
5. Build authenticated shell, Following/Discover, pagination, back restoration, search, saved and notifications. Add optimistic actions with failure rollback. Use fake data only behind explicit development fixtures.
6. Build compose/source/preview, local draft store, remote revision saving, conflict recovery and account isolation. Add attachment state machine, alt text, video accessibility metadata and upload retries. Gate publish against server preview and media readiness.
7. Add publish idempotency, edit/delete/replies, report/mute/block, profile editing and settings. Instrument failure diagnostics without logging private draft content.
8. Run ACCEPTANCE.feature scenarios, shared Markdown fixtures and API tests. Manually verify keyboard/VoiceOver/TalkBack, native back, text scaling, RTL, interrupted network and actual device media playback. Measure performance; record results and outstanding issues.

## Per-task completion record
- Requirement IDs implemented and exact screen states covered.
- Files changed and rationale for design deviations.
- Tests performed with concrete pass/fail results and device/viewport.
- Known limitations and next dependency; no unsupported claim of production readiness.

## Suggested first engineer prompt
“Using this kit as normative design input, implement tokens and the read-only PostCard + Reader vertical slice for Angular, SwiftUI and Compose. Follow FEED-002, READ-001, MD-001–007, A11Y-001–004 and UI-001. Use one shared canonical fixture response and demonstrate both themes, compact/expanded layouts, loading/unavailable states and large text. Do not implement publish yet. Return changed files, test evidence and any missing contract decision.”
