# Backstage docs — copy-paste examples

| File | Purpose |
|------|---------|
| **[backstage_host.example.py](backstage_host.example.py)** | **Start here** — copy to `yourapp/backstage_host.py` (nav, overrides, editor meta, preview) |
| [settings_snippet.py](settings_snippet.py) | Wire `BACKSTAGE` in `settings.py` |
| [host_singleton.py](host_singleton.py) | Abstract singleton page model |
| [host_seo_mixin.py](host_seo_mixin.py) | SEO tab field definitions |
| [host_cms_api_utils.py](host_cms_api_utils.py) | DRF `get_singleton`, media URL helpers for public CMS APIs |
| [host_singleton_viewset.py](host_singleton_viewset.py) | Read-only `ViewSet.list` for singleton pages |

Human onboarding: [../integration.md](../integration.md).

All `BACKSTAGE` keys: [../reference/configuration.md](../reference/configuration.md).
