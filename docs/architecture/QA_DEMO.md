<!-- Optional topic: copy when the product has QA quick-login or demo seed. Never enable in production. -->

# QA demo (optional)

[Product]-specific non-production helpers (quick login, demo seed, shared QA password). **Never enable in production.**

**Environment contract:** [DEPLOYMENT_ENVIRONMENTS.md](DEPLOYMENT_ENVIRONMENTS.md) (`APP_ENV`, `DEBUG`, `DEMO_ENABLED`).

## What it does

- [Describe API catalog / seed command / SPA panel.]
- Stub: [examples/qa_accounts_stub.py](examples/qa_accounts_stub.py)

## Backend env (staging / local)

```bash
APP_ENV=staging
DEBUG=0
DEMO_ENABLED=true
# DEMO_DEFAULT_PASSWORD=your-qa-password
```

## Frontend env (if SPA)

```bash
# VITE_DEMO_ENABLED=true   # staging build only
# VITE_DEMO_DEFAULT_PASSWORD=...
```

## Commands

```bash
# manage.py seed_demo_data / set_qa_passwords / etc. — refuse when DEMO_ENABLED=0
```

## Security

- Feature off by default; API returns **404** when disabled when applicable.
- No `demo_*/QA.md` or per-app README — keep this file as the single runbook.

## Related docs

- Hub: [ARCHITECTURE.md](../ARCHITECTURE.md)
- Env keys: [CONFIGURATION.md](../CONFIGURATION.md)
- Product invariants: [AGENTS.md](../../AGENTS.md)
