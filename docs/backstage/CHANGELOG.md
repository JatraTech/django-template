# Backstage docs changelog

## 2026-10-02

- **BPI-aligned backstage:** Package matches [bpi-backend](https://github.com/JatraTech/django-template) factory behavior—inline-only page children, editable stacked/tabular inlines on parents, `ADMIN_OVERRIDES` for customization.
- **Removed:** Hub inlines, `INLINE_RELATIONS`, `INLINE_HUB`, and `STANDALONE_CHILD_MODELS` compiler. Hosts that need custom inlines should use `ADMIN_OVERRIDES` (see [integration.md](integration.md)).

## 2026-09-29

- **INLINE_RELATIONS** and hub modes were added to django-template only; superseded by the BPI-aligned model above.
