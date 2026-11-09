# STMTS

Initial engineering increment based on `docs/STMTS_Engineering_Spec_v1.md` and the unchanged designer kit under `design/reference/`.

**Development prototype. M0 and M1 are in progress.** The rounded Quote v1.1 identity is adopted in web navigation/favicons. Task 2 parser fidelity is complete within its read-only scope; native/browser acceptance remains open. The Angular card and reader consume a canonical response from a Django/DRF development fixture endpoint. No accounts, real feed, publishing, storage, or media pipeline exist yet. Native projects are initial text-projection scaffolds, not verified apps.

## Start the API and web

Requires Python 3.12 and Node 24.22.1 (or compatible Node 24).

```sh
python -m venv .venv
.venv/bin/pip install -r backend/requirements.lock
.venv/bin/python backend/serve_fixture.py
```

In another terminal:

```sh
cd web
npm ci
npm start -- --host 127.0.0.1 --proxy-config proxy.json
```

Open http://127.0.0.1:4200/ for the API-backed development card. Continue reading opens the article. `/?demo=1` explicitly selects the web-only static fixture. `/?id=00000000-0000-4000-8000-000000000000` demonstrates unavailable content. Toggle appearance using the header button.

`serve_fixture.py` intentionally starts a development-only, database-free read endpoint. It is not a production WSGI server. The normal Django configuration requires a secret outside development and PostgreSQL for future persistence. There is no seeded login because identity is not implemented.

## Git history

Work is committed on `main`. No remote is configured. The source archive includes the `.git` directory and a portable `stmts-history.bundle`; extract hidden files too. To restore history independently, run `git clone stmts-history.bundle stmts-restored`. See `docs/next-10-tasks.md` for the ordered plan.

## Checks

```sh
STMTS_DEVELOPMENT=1 .venv/bin/pytest -q
python scripts/sync_content_contract.py
python scripts/generate_tokens.py
.venv/bin/python scripts/generate_fixture.py
cd web
npm run generate:api
npm run build
```

Python dependencies are pinned in `backend/requirements.lock`; npm dependencies in `web/package-lock.json`. CI runs the parser/API suite, generation drift checks and Angular production compilation. Production web builds exclude the static development JSON. The Django fixture endpoint returns 404 outside explicit development mode. Native release code does not load demo posts, but release packaging/distribution is not configured.

## Native development

- iOS/iPadOS: open `ios/Package.swift` to inspect the SwiftUI module. Generate an app project from `ios/project.yml` with XcodeGen, then open STMTS.xcodeproj in Xcode. The app uses a DEBUG-only shared fixture and native NavigationStack. Signing and device verification are pending.
- Android: open `android/` in Android Studio. The initial Gradle files use Java 17, SDK 36, Kotlin 2.2.20 and Compose. A checked-in wrapper, resolved dependency locks and a verified build remain pending. Demo loading is restricted to BuildConfig.DEBUG.
- Native renderers currently project rich blocks into text; links, tables, lists, inline marks, themes and accessibility parity are not complete. Do not claim T-01 or native acceptance passed.

## Local services for the next increment

Set POSTGRES_PASSWORD and run `docker compose -f infra/compose.yaml up -d`. PostgreSQL, Redis and RabbitMQ configuration is supplied, but Docker was unavailable during implementation and these service definitions were not started here. API workers/outbox integration will come with persistence. No SQLite substitution or database concurrency claim is made.

See `docs/implementation-status.md` for evidence and remaining work. The next dependency is completing canonical schema/rendering parity and native build gates before identity or publishing.


## Parser boundary

`backend/content/parser.py` accepts unchanged Unicode source and produces the strict canonical content tree. It normalizes newlines only for parsing/spans; task state is structured, IDs are opaque and previous-tree reuse must be scoped by trusted owner/document context. Optional trusted attachment resolvers validate a manifest; no upload or fetch endpoint exists.

Runtime defaults: 50,000 original code points, 2,000 canonical blocks, 12 block levels, 20,000 conversion-node allocations, 64 inline levels and a two-second cooperative processing budget. `content.worker.parse_isolated` additionally offers a configurable isolated subprocess with a 256 MiB virtual-memory cap and five-second wall deadline by default. It is tested on this Linux environment; the fixture API does not invoke it and no production parser consumer exists yet. A deployment adapter must use that boundary (or equivalent process isolation), install its own trusted media resolver and configure limits for its platform. Source is sent via stdin, not process arguments or logs.

The pinned `regex` dependency supplies Unicode grapheme boundaries for excerpts. Reading time remains the approximate 220-word/minute MVP rule. The shared canonical corpus is a reviewed expectation artifact; CI does not regenerate it from parser output. Fixture post generation reconciles previous IDs so regeneration remains stable.


## DreamHost hosting

See [DreamHost deployment](docs/dreamhost-deployment.md) for the GitHub Actions workflow, required SSH secrets/variables and rollback procedure. Shared hosting supports the explicit `build:shared-preview` static demonstration only. The planned live backend and SSR require suitable persistent-process/database hosting.
