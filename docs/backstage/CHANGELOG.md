# Backstage docs changelog

## 2026-09-29

- **INLINE_RELATIONS**: unified host config for parent → child inlines (`default_stacked`, `default_tabular`, `hub_tabular`, `hub_stacked`); compiles standalone children and admin overrides at startup.
- **Hub inlines**: read-only summary on parent forms with links to standalone child admin; documented in [features/hub-inlines.md](features/hub-inlines.md).
- **Hub primary tabs**: hub panels can share the parent’s fieldset tab nav (`hub_primary_tab` / `"primary_tab": false` to opt out).
- **Hub Add link**: footer uses `hub-add-link` (real `href`) so `app.js` does not treat Add as an in-page `#` row template.
- **Hub table layout**: tabular title row skipped for hub; pk/fk in main row; last-row border cleanup.
- **INLINE_HUB**: legacy; prefer `INLINE_RELATIONS` for new projects.
