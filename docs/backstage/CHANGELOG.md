# Backstage docs changelog

## 2026-10-02 (package sync)

- **Package re-aligned** with Caissa K12, BPI, and Sotherly: hub inlines, `INLINE_RELATIONS` compiler, `primary_tab_slug` (hub tab merged into parent fieldset tabs), scrollable fieldset tabs with horizontal wheel scroll.
- **Branding:** `branding_defaults_from_config()` seeds new `BackstageSettings` rows; migration `0002_backfill_branding_from_config` one-time backfill from `BACKSTAGE` SITE_* when DB fields are empty; display uses DB only via `resolve_branding_field` / `resolve_text` (cleared fields stay empty).
- **Admin UX:** Image preview checkerboard/border styling; dashboard welcome title respects resolved site header.

## 2026-10-02 (earlier note — superseded)

- The short-lived “BPI-aligned” doc that removed hub/`INLINE_RELATIONS` is **superseded** by the package sync above. Prefer `INLINE_RELATIONS` for parent→child edges; use `ADMIN_OVERRIDES` for one-off tweaks.

## 2026-09-29

- **INLINE_RELATIONS** and hub modes were added to django-template only; later consolidated into the shared package across hosts.
