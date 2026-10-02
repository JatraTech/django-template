# Hub inlines

When a parent page owns many child records (press releases, team members, etc.), editable tabular inlines on the parent form are often too cramped. **Hub mode** shows a read-only summary on the parent with **Edit** / **Delete** links to standalone admin screens and an **Add** / **View all** footer.

## Configuration

Prefer a single `INLINE_RELATIONS` entry per parent → child edge (see [integration.md](../integration.md)). Modes:

- `hub_tabular` — read-only table + Actions column
- `hub_stacked` — read-only stacked cards; Edit/Delete in the title row

Set `standalone_child: True` so the child model stays registered for full changelist/change views (required when the child has a single parent FK in the same app).

## Primary tabs (parent fieldset tabs)

On parents that use tabbed fieldsets (`"classes": ["tab"]` on each fieldset in `ADMIN_OVERRIDES`), hub relations are shown as **additional tabs** in the same underline nav as Page / SEO—not a separate heading and card below the page block. The hub table and footer sit inside that tab panel.

Opt out per relation with `"primary_tab": false` (renders the legacy layout below fieldsets). This is separate from `InlineModelAdmin.tab` (the pill “General + inline” nav).

## Add link vs in-page row

Hub **Add** uses the `hub-add-link` class and a normal admin URL (`href`), not `add-row` with `href="#"`. Backstage’s `addInlineTemplateHandler` skips links whose `href` is not `#`, so Add navigates to the child add form instead of inserting a blank inline row.

## Default editable inlines

Reverse FKs **not** listed in `INLINE_RELATIONS` keep the factory default: **stacked**, editable on the parent form (e.g. paragraph blocks on a press release).

## Extension

`HubInlineMixin.get_hub_template_context(request)` is reserved for future django-template admin panels.
