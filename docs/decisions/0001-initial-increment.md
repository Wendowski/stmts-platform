# ADR 0001: Initial read-only increment

Accepted for development, 8 November 2026.

Follow the architect's M0/M1 starting scope and Paper / Forest visual baseline. Keep the complete designer kit unchanged. Establish a read-only contract without adding mutation endpoints. The API's only data source is an explicit development fixture; real public reading from PostgreSQL belongs to M2.

A conservative prototype node schema is supplied. It is not yet the final discriminated schema: per-variant required attributes, task nodes, attachment nodes, nesting limits at schema validation, spans on inline nodes and edit-stable identity under duplicate-block insertion remain M1 blockers. Parser depth and block-count checks are implemented separately.

Native starter views use a text projection while toolchains and rich renderer parity are incomplete. This is recorded as partial implementation, not a substitution for native acceptance. Browser card/reader selection uses query parameters for this increment; canonical `/p/:id/:slug` routing, profiles, navigation restoration and SSR metadata are pending M2 work.

No external beta or release is authorized by this increment. The policy decisions in engineering spec section 16 remain open.
