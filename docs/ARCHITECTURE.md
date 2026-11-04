# [Product] architecture (hub)

**django-template (this repo):** reference Django API and **Backstage** admin host. Day-to-day invariants: [AGENTS.md](../AGENTS.md). Env and Docker: [CONFIGURATION.md](CONFIGURATION.md). Full index: [README.md](README.md).

For a new product, replace the paragraph above with what your API does (tenancy model, main subsystems). Keep this file a **table of contents** only.

## Topics

| Topic | Document |
|-------|----------|
| Example topic (rename when copying) | [architecture/EXAMPLE_TOPIC.md](architecture/EXAMPLE_TOPIC.md) |
| Backstage CMS (django-template host only) | [architecture/BACKSTAGE.md](architecture/BACKSTAGE.md) |
| QA demo (optional; non-production) | [architecture/QA_DEMO.md](architecture/QA_DEMO.md) |
| Deployment environments | [architecture/DEPLOYMENT_ENVIRONMENTS.md](architecture/DEPLOYMENT_ENVIRONMENTS.md) |

Add a row per real topic (`SITES.md`, `PLANS.md`, …). Do not duplicate topic body in this file — edit the topic doc under `architecture/`.

## What not to document here

- Env, Docker, Redis — [CONFIGURATION.md](CONFIGURATION.md).
- Backstage implementation detail — [backstage/](backstage/) (django-template only).
