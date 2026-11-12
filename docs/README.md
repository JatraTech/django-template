# django-template documentation

## Read order

1. Repo [README.md](../README.md) — install, run, deploy, verification
2. [AGENTS.md](../AGENTS.md) — invariants, app map, commands
3. [CONFIGURATION.md](CONFIGURATION.md) — env, Docker, Redis
4. [ARCHITECTURE.md](ARCHITECTURE.md) — hub (links to topics below)
5. Topic files in `architecture/` as needed

## Documentation layout

When you fork this template for a product backend, keep the same shape:

```text
README.md          # Procedural: install, run, deploy
AGENTS.md          # Agent/human invariants and commands
docs/README.md     # This index
docs/CONFIGURATION.md
docs/ARCHITECTURE.md   # Hub only — links to topics
docs/architecture/     # One file per topic (UPPERCASE.md)
```

Cross-repo packages: link [django-jt](https://github.com/JatraTech/django-jt) and [django-backstage](https://github.com/JatraTech/django-backstage) on GitHub, not monorepo paths.

## Index

| Document | When to read |
|----------|----------------|
| [CONFIGURATION.md](CONFIGURATION.md) | `.env`, compose, CORS, external Postgres |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Hub: what the backend covers + topic links |
| [architecture/EXAMPLE_TOPIC.md](architecture/EXAMPLE_TOPIC.md) | Example topic — copy/rename when bootstrapping |
| [architecture/BACKSTAGE.md](architecture/BACKSTAGE.md) | Backstage CMS on this reference host |
| [backstage/reference-host.md](backstage/reference-host.md) | Manual QA checklist for the `sample` app |
| [architecture/QA_DEMO.md](architecture/QA_DEMO.md) | Optional QA / demo runbook stub (copy when needed) |
| [architecture/DEPLOYMENT_ENVIRONMENTS.md](architecture/DEPLOYMENT_ENVIRONMENTS.md) | Local / staging / production contract |
| [architecture/product_api_patterns.md](architecture/product_api_patterns.md) | django-jt analytics / export (reference) |

Architecture depth lives under `architecture/`; the hub file [`ARCHITECTURE.md`](ARCHITECTURE.md) links each topic.
