# STMTS

Initial engineering increment based on `docs/STMTS_Engineering_Spec_v1.md` and the unchanged designer kit under `design/reference/`.

**Development prototype. M0 and M1 are in progress.** The Angular card and reader consume a canonical response from a Django/DRF development fixture endpoint. No accounts, real feed, publishing, storage, or media pipeline exist yet. Native projects are initial text-projection scaffolds, not verified apps.

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

## Checks

```sh
STMTS_DEVELOPMENT=1 .venv/bin/pytest -q
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
