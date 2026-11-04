<!-- Copy this file to docs/architecture/<TOPIC>.md (e.g. SITES.md), replace placeholders, and add a row in docs/ARCHITECTURE.md.
     Standard slots (do not rename): APP_STRUCTURE, UI_PATTERNS, QA_DEMO — use product names (SITES, PLANS, …) for domain topics. -->

# [Topic name]

One-line scope: what this topic covers and when an agent should open this file.

## Overview

[Product]-specific behavior, hosts, or boundaries. Link to code under `app/` or Django apps — use repo-root paths, not doc files under `django-app/`.

## Key modules

| Area | Path |
|------|------|
| [Example] | `app/...` or `myapp/...` |

## API surface (if applicable)

| Endpoint / area | Role |
|-----------------|------|
| `GET /api/v1/...` | [Describe] |

## Related docs

- Hub: [ARCHITECTURE.md](../ARCHITECTURE.md)
- Product invariants: [AGENTS.md](../../AGENTS.md)
- Env: [CONFIGURATION.md](../CONFIGURATION.md)
