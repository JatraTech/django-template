# Troubleshooting and QA

## Integration check command

```bash
python manage.py check_backstage_integration
```

Validates `INSTALLED_APPS` order, `BACKSTAGE` dict, theme URL, migrations, and preview URL warnings. Run after setup and in CI if desired.

## Preview

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Broken iframe icon | Frontend not running | Start Vite/dev server |
| Wrong page | Callback path mismatch | Fix `resolve_preview_route` in `backstage_host.py` |
| Browser: “Request header field x-preview-token is not allowed…” (CORS preflight) | `CORS_ALLOW_HEADERS` missing `x-preview-token` | Add tuple in host `settings.py` (see [../features/preview-and-frontend.md](../features/preview-and-frontend.md) or [../examples/settings_snippet.py](../examples/settings_snippet.py)) |
| 401/403 on API in iframe | Missing CORS header or invalid token | Add `x-preview-token` to `CORS_ALLOW_HEADERS`; check preview token TTL |
| Stale content | Expected | Preview shows **saved** DB state — save form first |
| Empty preview panel | Callback returned `None` | Implement route for model class |

Set **Admin appearance → Preview → Frontend URL** to match `FRONTEND_URL`.

## `AlreadyRegistered` on startup

You registered a model in `admin.py` that Backstage already registered.

**Fix:** `admin.site.unregister(Model)` before `register`, or remove duplicate `@admin.register`. See [../features/customization.md](../features/customization.md).

## Missing SEO tab

Model lacks editable fields whose names match `SEO_FIELD_NAMES` (defaults in `conf.py`). Add fields or override `BACKSTAGE["SEO_FIELD_NAMES"]`.

## Rich text is plain textarea

- Field name not in `RICH_TEXT_FIELD_NAMES` or matching `RICH_TEXT_SUFFIXES`.
- `django-tinymce` not installed or `TINYMCE_DEFAULT_CONFIG` missing.

## Missing editor labels

Add entries to `FIELD_EDITOR_META` for that lowercase model name. Custom `ModelAdmin` without `EditorMetadataMixin` will not apply meta.

## Form fields look flush (no padding) in admin

Model fields get Backstage widgets from `backstage/overrides.py`. Extra fields on a custom `ModelAdmin` form or `ModelForm.Meta.widgets` must use `BackstageAdmin*` classes from `backstage/widgets.py` (for example `BackstageAdminTextareaWidget`, `BackstageAdminCheckboxSelectMultipleWidget`). Raw `forms.Textarea` or `forms.CheckboxSelectMultiple` skip theme padding and look wrong under Tailwind preflight.

## Sidebar link visible but change view returns 403

Sidebar items use the same rule as the Django app index: `ModelAdmin.has_view_permission(request)` on the registered admin class. If a link appears but the view is forbidden, check django permissions and any custom `has_view_permission` / `has_module_permission` on that admin. If a link should be hidden, fix the admin permission methods or remove the model from `NAV_GROUPS.models` (allowlist only — it does not grant access).

## Primary button text invisible in changelist / `list_display`

`admin-theme.css` styles most `#content-main a[href]` as link-colored text. Anchors styled only with `bg-primary-600` keep that link color, so label text can disappear on a filled button. Use the Backstage button component in templates, or `format_html` with classes such as `backstage-control`, `text-primary-foreground`, and `bg-primary-600` together.

## Theme / CSS broken after edit

Rebuild admin CSS:

```bash
cd backstage && npm install && npm run build:css
```

Hard-refresh browser after changing `styles.css` or Tailwind classes.

## Integration check

```bash
python manage.py check_backstage_integration
```

BPI product tests: `uv run pytest core/tests app/tests -q` (default `app.settings`).

**Sample admin + themed UI:** this repo (`/admin/`, `sample` models, System → Admin appearance).

## Manual QA (after theme changes)

1. Changelist — row dividers, Actions column
2. Change form + preview split pane
3. User edit — permissions, inlines
4. Filter sidebar panels
5. Dark mode on the above
