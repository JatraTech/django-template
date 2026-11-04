# [Product] backend documentation

Replace `[Product]` with your product name. Customize the index table when you add topics.

## Read order

1. Repo [README.md](../README.md) — install, run, deploy
2. [AGENTS.md](../AGENTS.md) — invariants, app map, commands
3. [CONFIGURATION.md](CONFIGURATION.md) — env, Docker, Redis
4. [ARCHITECTURE.md](ARCHITECTURE.md) — hub (links to topics below)
5. Topic files in `architecture/` as needed

## Index

| Document | When to read |
|----------|----------------|
| [CONFIGURATION.md](CONFIGURATION.md) | `.env`, compose, CORS, external Postgres |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Hub: what the backend covers + topic links |
| [architecture/EXAMPLE_TOPIC.md](architecture/EXAMPLE_TOPIC.md) | Example topic — copy/rename when bootstrapping |
| [architecture/BACKSTAGE.md](architecture/BACKSTAGE.md) | **django-template only:** Backstage CMS host |
| [architecture/QA_DEMO.md](architecture/QA_DEMO.md) | Optional QA / demo runbook stub (copy when needed) |
| [architecture/DEPLOYMENT_ENVIRONMENTS.md](architecture/DEPLOYMENT_ENVIRONMENTS.md) | Local / staging / production contract (`APP_ENV`, `DEBUG`, `DEMO_ENABLED`) |

Architecture depth lives under `architecture/`; the hub file [`ARCHITECTURE.md`](ARCHITECTURE.md) links each topic.
