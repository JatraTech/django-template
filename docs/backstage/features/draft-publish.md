# Draft, publish, and preview

## Product rules

- Models in `BACKSTAGE["DRAFT_PUBLISH"]["models"]` with duplicate-row support (`live_version` / `DraftPublishDuplicateRowMixin`) use **Save draft** and **Publish**.
- Split-pane **preview** is enabled only for those models when `resolve_preview_route` returns a path. Host projects only maintain route mapping in `backstage_host.py` and frontend URL settings.
- Models not in the allowlist keep direct **Save** behavior and no draft-gated preview pane.

## Configuration

```python
BACKSTAGE = {
    "DRAFT_PUBLISH": {
        "enabled": True,
        "models": ["core.blogpost"],
    },
    "PREVIEW_ROUTE_CALLBACK": "yourapp.backstage_host.resolve_preview_route",
}
```

## Blog (duplicate row)

- **Live row:** `live_version` is null, `is_published=True` for the public site.
- **Lazy draft:** opening a published post with **no** draft row stays on the **live** change form. Banner explains both paths; footer shows **Save**, **Save and continue editing**, and **Save draft & show preview** (no Publish, no Discard, no Edit live). **Save** / **Save and continue** update the live row immediately. **Save draft & show preview** (`_start_draft`) creates a draft row, writes edits there (live content unchanged), and redirects to the draft editor.
- **Draft row:** `live_version` → live pk. If a draft already exists, opening the published post redirects to that draft. Full draft chrome (**Edit live** in banner, **Discard draft** in footer, **Save draft & update preview**, **Publish**) applies only on the draft row.
- **Publish:** saves the change form, copies draft fields to live, deletes the draft row, redirects to the changelist. Confirmation modal submits the main form with `_publish` (one step: save + publish). The separate **`/publish/`** POST still publishes the last saved DB row (fallback for tests/tools; not used by the admin UI). **Publish** is always available on draft rows; no session “save draft first” gate.
- **Discard draft:** removes the draft row only; the live post stays published. **Discard draft** footer button on draft rows (confirm dialog explains live is kept).
- **Edit live (advanced):** from the draft banner, **Edit live version (advanced)** opens the live row with `?edit_live=1`. Saves update the **live site immediately** and skip Publish. If a pending draft exists, **Save** / **Save and continue** open a confirm dialog: updating live removes the unpublished draft (no divergent copies). With no pending draft, edit-live save behaves as a normal immediate live update. After save, the form stays in edit-live mode so you are not bounced back into a stale draft.
- **API:** public reads live published rows; preview token returns the draft row for detail by token pk.

## Editor UX (admin)

Draft rows are edited on their own change URL (redirect from live when a draft exists). The live change form does **not** expose a `draft_copies` tabbed inline—only inner fieldset tabs (Content, Publishing, SEO).

Action placement:

| Action | No draft yet (live) | Draft copy | Edit live | Unpublished |
|--------|---------------------|------------|-----------|-------------|
| Save draft & show preview | Footer (outlined, `_start_draft`) | — | — | — |
| Save draft & update preview | — | Footer (primary) | — | Footer (primary) |
| Save / Save and continue | **Save** primary; **Save and continue** outlined (live update) | — | **Save** primary; **Save and continue** outlined | — |
| Publish | — | Footer (secondary, confirm) | — | Footer (secondary, confirm) |
| Discard draft | — | Footer | — | — |
| Delete | Footer (outline danger) | — | Footer (outline danger) | Footer (outline danger) |
| Close | Footer | Footer | Footer | Footer |

- **Change form (live, no draft yet):** informational banner; **Save** / **Save and continue** update live immediately; **Save draft & show preview** starts a draft and opens the full draft editor.
- **Change form (draft):** banner explains draft vs live (**Edit live** link only); subtitle `(draft)` when editing a draft copy. Footer: **Discard draft**, primary **Save draft & update preview**, secondary **Publish**.
- **Change form (edit live):** warning banner; **Save** (primary) and **Save and continue editing** (outlined). **Delete** (outline danger) beside **Close** when permitted. Preview reflects the live page after save.
- **Changelist:** **Status** and **Draft pending** on live rows; row **Edit** opens the draft when one exists.

### Footer visuals

- One filled **primary** (brand accent) action per change-form mode. On **live, no draft** and **edit live**, that primary is **Save** (immediate live update). On the **draft copy**, primary is **Save draft & update preview**.
- Other saves on those screens use outlined **`default`** buttons at **sm** size with Material icons (not ghost).
- **Delete** and **Discard draft** use **danger-outline** (red border/text, not solid fill) so they do not compete with the accent primary.
- **Publish** in the draft footer is outlined **default** until confirmed; the confirm modal uses a primary **Publish** button.

## Future: singleton snapshot

About/Home pages will use a published JSON snapshot strategy (not duplicate rows). Same allowlist and preview rules.

## Verify

```bash
python manage.py check_backstage_integration
```

Warns when allowlisted models lack `live_version` or preview route mapping.
