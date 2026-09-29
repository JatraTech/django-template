# Configuration reference

Settings merge: **`get_config()`** = `CONFIG_DEFAULTS` deep-merged with Django **`BACKSTAGE`** (`backstage/settings.py`).

Branding fields also resolve **DB first** via `BackstageSettings` and `branding.py` (site title, colors, logos, `frontend_url`). See resolution table below.

Machine-readable key list: [config-keys.yaml](config-keys.yaml) (keep in sync with this reference).

**Full annotated template:** [../examples/backstage_host.example.py](../examples/backstage_host.example.py).

## Top-level `BACKSTAGE` keys

| Key | Type | Purpose |
|-----|------|---------|
| `SITE_TITLE` | str | Browser title / branding |
| `SITE_HEADER` | str | Header text |
| `SITE_SUBHEADER` | str | Subheader |
| `SITE_VERSION` | str | Optional version label |
| `SITE_DROPDOWN` | list | Extra header links |
| `SITE_URL` | str | Default public site URL (preview fallback) |
| `SITE_VIEWS` | list | Custom admin views |
| `SITE_ICON` / `SITE_SYMBOL` / `SITE_LOGO` | various | Legacy branding assets |
| `SITE_FAVICONS` | list | Favicon definitions |
| `SHOW_HISTORY` | bool | Object history UI |
| `SHOW_VIEW_ON_SITE` | bool | View on site link |
| `SHOW_LANGUAGES` | bool | Language switcher |
| `SHOW_BACK_BUTTON` | bool | Back navigation |
| `SHOW_UI_WARNINGS` | bool | Backstage UI warnings |
| `LANGUAGE_FLAGS` | dict | Flag map for languages |
| `FORMS` | dict | Widget CSS class map |
| `COLORS` | dict | Default palette tokens (often overridden in DB) |
| `GLOBAL_CALLBACK` | str | Import path hook |
| `DASHBOARD_CALLBACK` | str | `(request, context) -> context` after dashboard widgets built |
| `DASHBOARD` | dict | Widget layout, stats, quick actions (see below) |
| `DASHBOARD_TEMPLATE` | str or null | Full index template override; null = package `backstage/dashboard/index.html` |
| `ENVIRONMENT` / `ENVIRONMENT_TITLE_PREFIX` | str | Environment badge |
| `NAV_GROUPS` | dict | Sidebar groups → app labels |
| `MODEL_ICONS` | dict | Lowercase model name → Material icon |
| `MODEL_LABELS` | dict | Lowercase model name → nav label |
| `PREVIEW_ROUTE_CALLBACK` | str | Import path `(obj) -> path or None` |
| `ADMIN_OVERRIDES` | dict | Model class name → ModelAdmin attrs |
| `FIELD_EDITOR_META` | dict | Model → field → `label` / `help_text` |
| `TAB_DESCRIPTIONS` | dict | Model → tab name → intro text |
| `SKIP_APP_LABELS` | list or null | Skip autodiscover/nav; null = package default |
| `SEO_FIELD_NAMES` | list or null | SEO tab fields; null = package default |
| `RICH_TEXT_FIELD_NAMES` | list or null | Exact TinyMCE fields |
| `RICH_TEXT_SUFFIXES` | list or null | Suffix match for TinyMCE |
| `STYLES` / `SCRIPTS` | list | Extra static assets |
| `ACCOUNT` | dict | Account nav |
| `LANGUAGES` | dict | Language nav |
| `COMMAND` | dict | Command palette |
| `SIDEBAR` | dict | `navigation`, `show_search`, `group_collapse`, … |
| `TABS` | list | Custom admin tabs |
| `LOGIN` | dict | Login page options |

### `DASHBOARD` nested keys

| Key | Purpose |
|-----|---------|
| `enabled` | Default `true`. When `false`, admin home uses legacy `admin/index.html` (model list + recent actions). |
| `layout` | Ordered widget ids: `welcome`, `stats`, `quick_actions`, `my_drafts`, `recent_activity` |
| `welcome` | Optional `{title, body}` overrides (defaults use `SITE_HEADER` / generic body) |
| `stats` | List of stat cards (`model`, `filter`, `count_callback`, `link`, `icon`, `accent`, …) |
| `quick_actions` | List of shortcuts (`model`, `action`: `add` \| `changelist` \| `change`, `singleton`) |
| `my_drafts` | `{limit}` — draft copies from `DRAFT_PUBLISH.models` |
| `recent_activity` | `{limit}` — current user admin log |
| `show_app_list` | When `true`, append legacy app/model table below widgets |

Default layout when unset: `welcome`, `recent_activity` only.

### `SIDEBAR` nested keys

| Key | Values | Purpose |
|-----|--------|---------|
| `navigation` | list | Full manual nav (replaces auto when non-empty) |
| `group_collapse` | `open` \| `collapsed` \| `dynamic` | Nav group expand behavior |
| `show_search` | bool | Sidebar search |
| `show_all_applications` | bool | All apps link |

## `conf.py` accessors

| Function | `BACKSTAGE` key |
|----------|-----------------|
| `get_skip_app_labels()` | `SKIP_APP_LABELS` |
| `get_seo_field_names()` | `SEO_FIELD_NAMES` |
| `get_rich_text_field_names()` | `RICH_TEXT_FIELD_NAMES` |
| `get_rich_text_suffixes()` | `RICH_TEXT_SUFFIXES` |
| `get_sidebar_group_collapse()` | `SIDEBAR.group_collapse` |
| `get_field_editor_meta(model)` | `FIELD_EDITOR_META` |
| `get_tab_descriptions(model)` | `TAB_DESCRIPTIONS` |
| `get_model_label(model)` | `MODEL_LABELS` |

## Resolution order (branding & preview URL)

| Concern | 1 | 2 | 3 |
|---------|---|---|---|
| Site title, accent, logos, theme | `BackstageSettings` (DB) | `BACKSTAGE` | `defaults.py` / env |
| Public / preview base URL | DB `frontend_url` | `BACKSTAGE["SITE_URL"]` | `FRONTEND_URL` env |
| API docs link | `BACKSTAGE["API_DOCS_URL"]` | `BACKEND_URL` env | — |

Configure live values under **System → Admin appearance** (model `BackstageSettings`).

## Label and help text hierarchy (admin forms)

Bottom to top (later wins for that property):

1. Model `verbose_name` / `help_text`
2. Django `ModelAdmin.formfield_for_dbfield` (mixins, widgets)
3. **`FIELD_EDITOR_META`** — only keys you set (`label`, `help_text`)
4. Custom admin code after `super()` in `get_form` / `formfield_for_dbfield`

Tab intros: **`TAB_DESCRIPTIONS`** on fieldsets only (not model fields).

Changelist column headers use model meta unless `list_display` uses callable labels.

## Environment variables (typical host)

| Variable | Used for |
|----------|----------|
| `FRONTEND_URL` | Preview iframe, `SITE_URL` |
| `BACKEND_URL` | API docs dropdown |

## Related Django settings (host, not `BACKSTAGE`)

| Setting | Purpose |
|---------|---------|
| `TINYMCE_DEFAULT_CONFIG` | Rich text toolbar |
| `CORS_ALLOW_HEADERS` | Include `x-preview-token` for preview |
