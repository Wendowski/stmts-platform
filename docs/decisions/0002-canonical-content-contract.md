# ADR 0002: Discriminated canonical content contract

Accepted for development, 8 November 2026. Covers CONTENT-002, MD-006/007 and API-002.

`contracts/content.schema.json` owns the canonical node definitions. Each variant has a literal `type`, exact allowed attributes and required variant metadata. Containers cannot hide arbitrary text payloads. Paragraphs/headings/cells contain inline nodes; lists contain list items; tables contain sections/rows/cells; top-level content contains document blocks. Leaves have no children. Headings require depth 1–6; links require an allowed-scheme destination; media references use an attachment UUID, never a supplied remote URL.

`scripts/sync_content_contract.py` projects the schema into OpenAPI with local component references. OpenAPI TypeScript generation uses `--array-length` so empty leaf arrays and fixed-length source spans do not widen into `unknown[]`. Generated transport types remain the web renderer's model source.

The existing uniform id/text/children shape remains compatible with the initial clients. Block IDs are bounded opaque strings. Block line spans are zero-based, half-open ranges; table wrapper placeholder spans remain documented until task 2. Structural schemas do not prove attachment ownership/readiness, contextual nesting safety, total node limits, span ordering, unique IDs or accessibility metadata eligibility. Those checks belong to parser/domain services; the schema must not be treated as an authorization boundary.

Task-item and media variants define the target contract. The current parser does not emit authorized media, and its checkbox state is still missing. No media fetching or publication is enabled by adding these shapes.

`contracts/fixtures/canonical-cases.json` preserves the original 11 sources and readable rendering expectations and adds full canonical expected documents. Parser comparisons ignore allocation-specific IDs and source spans so future identity/span corrections do not rewrite semantic expectations. The task-list target explicitly includes checked/unchecked states; its single known gap is narrowly asserted against the current legacy shape before being marked expected-failure. Unexpected differences still fail. Expected trees are reviewed source artifacts, not regenerated from the parser in CI.

This closes task 1's contract/fixture scope. Full stmts-md/1 conformance, parser resource enforcement, native rendering parity and production readiness remain open.
