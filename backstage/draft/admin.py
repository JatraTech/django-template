from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from backstage.draft.conf import is_draft_publish_model
from backstage.draft.services import DraftPublishService


def _request_edit_live(request: HttpRequest) -> bool:
    value = request.GET.get("edit_live") or request.POST.get("_edit_live")
    return value in ("1", "true", "True")


def _draft_saved_session_key(model: type[models.Model], pk: int) -> str:
    return f"backstage:draft_saved:{model._meta.label_lower}:{pk}"


def _draft_publish_ready(request: HttpRequest, model: type[models.Model], pk: int) -> bool:
    return bool(request.session.get(_draft_saved_session_key(model, pk)))


def _mark_draft_saved(request: HttpRequest, model: type[models.Model], pk: int) -> None:
    request.session[_draft_saved_session_key(model, pk)] = True
    request.session.modified = True


def _clear_draft_saved(request: HttpRequest, model: type[models.Model], pk: int) -> None:
    request.session.pop(_draft_saved_session_key(model, pk), None)
    request.session.modified = True


def _uses_draft_workflow_footer(obj, edit_live: bool) -> bool:
    if edit_live:
        return False
    if obj is None:
        return True
    if obj.is_draft_copy:
        return True
    if obj.is_live_row and obj.is_published:
        return False
    return obj.is_live_row and not obj.is_published


def _should_start_draft_from_live(request: HttpRequest, obj) -> bool:
    return (
        "_start_draft" in request.POST
        and obj.is_live_row
        and obj.is_published
        and not _request_edit_live(request)
        and not obj.draft_copies.exists()
    )


def _publish_requested(request: HttpRequest) -> bool:
    return "_publish" in request.POST


def _can_publish_from_change_form(obj) -> bool:
    if obj is None:
        return False
    if obj.is_draft_copy:
        return True
    return obj.is_live_row and not obj.is_published


def _confirm_discard_pending_draft(request: HttpRequest) -> bool:
    return "_confirm_discard_pending_draft" in request.POST


def _edit_live_save_attempt(request: HttpRequest) -> bool:
    return "_save" in request.POST or "_continue" in request.POST


def _edit_live_blocked_by_pending_draft(request: HttpRequest, obj) -> bool:
    if obj is None or not hasattr(obj, "is_live_row"):
        return False
    if not _request_edit_live(request):
        return False
    if not obj.is_live_row:
        return False
    if not obj.draft_copies.exists():
        return False
    if not _edit_live_save_attempt(request):
        return False
    return not _confirm_discard_pending_draft(request)


class DraftPublishAdminMixin:
    """Save edits on draft rows; publish promotes to live. Redirect to draft only when one exists."""

    change_form_outer_before_template = "backstage/draft/change_form_banner.html"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_draft_publish_model(self.model) and getattr(self, "_restrict_to_live_rows", False):
            return qs.filter(live_version__isnull=True).prefetch_related("draft_copies")
        return qs

    def changelist_view(self, request, extra_context=None):
        if is_draft_publish_model(self.model):
            self._restrict_to_live_rows = True
            try:
                return super().changelist_view(request, extra_context)
            finally:
                self._restrict_to_live_rows = False
        return super().changelist_view(request, extra_context)

    def get_list_display(self, request):
        display = list(super().get_list_display(request))
        if not is_draft_publish_model(self.model):
            return display
        display = [name for name in display if name != "live_version"]
        extra = ("publication_status", "has_unpublished_draft")
        if not display:
            return list(extra)
        return [display[0], *extra, *display[1:]]

    @admin.display(description=_("Status"), ordering="is_published")
    def publication_status(self, obj):
        if not obj.is_published:
            return _("Unpublished")
        drafts = getattr(obj, "_prefetched_objects_cache", {}).get("draft_copies")
        if drafts is not None:
            if drafts:
                return _("Draft in progress")
        elif obj.draft_copies.exists():
            return _("Draft in progress")
        return _("Published")

    @admin.display(description=_("Draft pending"), boolean=True)
    def has_unpublished_draft(self, obj):
        drafts = getattr(obj, "_prefetched_objects_cache", {}).get("draft_copies")
        if drafts is not None:
            return bool(drafts)
        return obj.draft_copies.exists()

    def get_changelist_edit_pk(self, obj) -> int:
        if obj.is_live_row and obj.is_published:
            draft = obj.draft_copies.first()
            if draft is not None:
                return draft.pk
        return obj.pk

    def get_exclude(self, request, obj=None):
        excluded = list(super().get_exclude(request, obj) or [])
        if is_draft_publish_model(self.model) and "is_published" not in excluded:
            excluded.extend(["is_published", "live_version"])
        return excluded or None

    def get_form(self, request, obj=None, change=False, **kwargs):
        base_form = super().get_form(request, obj, change=change, **kwargs)
        if not is_draft_publish_model(self.model):
            return base_form

        class DraftPublishChangeForm(base_form):
            def clean(self):
                cleaned_data = super().clean()
                if _edit_live_blocked_by_pending_draft(request, obj):
                    raise ValidationError(
                        _(
                            "Confirm that you want to update the live site and remove "
                            "the unpublished draft before saving."
                        )
                    )
                return cleaned_data

        DraftPublishChangeForm.__name__ = base_form.__name__
        DraftPublishChangeForm.__qualname__ = base_form.__qualname__
        return DraftPublishChangeForm

    def get_urls(self):
        urls = super().get_urls()
        if not is_draft_publish_model(self.model):
            return urls
        info = self.model._meta.app_label, self.model._meta.model_name
        custom = [
            path(
                "<path:object_id>/publish/",
                self.admin_site.admin_view(self.publish_view),
                name=f"{info[0]}_{info[1]}_publish",
            ),
            path(
                "<path:object_id>/discard-draft/",
                self.admin_site.admin_view(self.discard_draft_view),
                name=f"{info[0]}_{info[1]}_discard_draft",
            ),
        ]
        return custom + urls

    def publish_view(self, request: HttpRequest, object_id: str):
        obj = self.get_object(request, object_id)
        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, self.model._meta, object_id)

        if not self.has_change_permission(request, obj):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied

        live = DraftPublishService.publish(obj)
        _clear_draft_saved(request, self.model, obj.pk)
        messages.success(request, _("Published successfully. The live site has been updated."))
        return self._redirect_to_changelist()

    def discard_draft_view(self, request: HttpRequest, object_id: str):
        if request.method != "POST":
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied

        obj = self.get_object(request, object_id)
        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, self.model._meta, object_id)

        if not self.has_change_permission(request, obj):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied

        if not obj.is_draft_copy:
            messages.error(request, _("Only draft copies can be discarded."))
        else:
            draft_pk = obj.pk
            DraftPublishService.discard_draft(obj)
            _clear_draft_saved(request, self.model, draft_pk)
            messages.success(
                request,
                _("Draft discarded. Unpublished edits were removed; the live post is unchanged."),
            )

        changelist_url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist",
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(changelist_url)

    def _append_edit_live_query(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        if not _request_edit_live(request):
            return response
        if not isinstance(response, HttpResponseRedirect):
            return response
        parsed = urlparse(response.url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["edit_live"] = "1"
        new_query = urlencode(query)
        new_url = urlunparse(parsed._replace(query=new_query))
        return HttpResponseRedirect(new_url)

    def save_model(self, request: HttpRequest, obj, form: Form, change: bool) -> None:
        if (
            is_draft_publish_model(self.model)
            and change
            and hasattr(obj, "is_live_row")
            and _should_start_draft_from_live(request, obj)
        ):
            draft = DraftPublishService.create_draft_from_live_form(obj, form)
            request._draft_publish_lazy_redirect_pk = draft.pk  # noqa: SLF001
            _mark_draft_saved(request, self.model, draft.pk)
            return
        super().save_model(request, obj, form, change)
        if (
            is_draft_publish_model(self.model)
            and change
            and hasattr(obj, "is_live_row")
            and obj.is_live_row
            and _request_edit_live(request)
            and _confirm_discard_pending_draft(request)
            and obj.draft_copies.exists()
        ):
            draft_pks = list(obj.draft_copies.values_list("pk", flat=True))
            DraftPublishService.discard_pending_drafts_for_live(obj)
            for draft_pk in draft_pks:
                _clear_draft_saved(request, self.model, draft_pk)
            messages.success(
                request,
                _("Live site updated. The unpublished draft was removed."),
            )

    def _redirect_to_draft_change(self, request: HttpRequest, draft_pk: int) -> HttpResponseRedirect:
        url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
            args=[draft_pk],
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    def _redirect_to_changelist(self) -> HttpResponseRedirect:
        changelist_url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist",
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(changelist_url)

    def response_change(self, request, obj):
        if is_draft_publish_model(self.model) and _publish_requested(request) and _can_publish_from_change_form(obj):
            draft_pk = obj.pk if obj.is_draft_copy else None
            DraftPublishService.publish(obj)
            if draft_pk is not None:
                _clear_draft_saved(request, self.model, draft_pk)
            messages.success(request, _("Published successfully. The live site has been updated."))
            return self._redirect_to_changelist()

        lazy_pk = getattr(request, "_draft_publish_lazy_redirect_pk", None)
        response = super().response_change(request, obj)
        if is_draft_publish_model(self.model):
            if lazy_pk is not None:
                self.message_user(
                    request,
                    _("Draft started. Continue editing below, then Publish when ready."),
                    messages.SUCCESS,
                )
                return self._redirect_to_draft_change(request, lazy_pk)
            if hasattr(obj, "is_draft_copy") and (obj.is_draft_copy or (obj.is_live_row and not obj.is_published)):
                _mark_draft_saved(request, self.model, obj.pk)
            response = self._append_edit_live_query(request, response)
        return response

    def response_add(self, request, obj, post_url_continue=None):
        response = super().response_add(request, obj, post_url_continue)
        if is_draft_publish_model(self.model) and obj is not None:
            _mark_draft_saved(request, self.model, obj.pk)
        return response

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if is_draft_publish_model(self.model) and object_id:
            obj = self.get_object(request, object_id)
            if (
                obj
                and obj.is_live_row
                and obj.is_published
                and request.method == "GET"
                and not _request_edit_live(request)
            ):
                draft = obj.draft_copies.first()
                if draft is not None:
                    draft_url = reverse(
                        f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                        args=[draft.pk],
                        current_app=self.admin_site.name,
                    )
                    return redirect(draft_url)

        extra_context = extra_context or {}
        if is_draft_publish_model(self.model):
            obj = self.get_object(request, object_id) if object_id else None
            edit_live = bool(obj and obj.is_live_row and obj.is_published and _request_edit_live(request))
            live_published_pending_draft = bool(
                obj and obj.is_live_row and obj.is_published and not edit_live and not obj.draft_copies.exists()
            )

            extra_context["draft_publish_enabled"] = True
            extra_context["draft_publish_custom_submit"] = True
            extra_context["edit_live_mode"] = edit_live
            extra_context["live_published_pending_draft"] = live_published_pending_draft
            extra_context["draft_workflow_footer"] = _uses_draft_workflow_footer(obj, edit_live)
            extra_context["pending_draft_pk"] = None

            if edit_live:
                extra_context["show_save"] = True
                extra_context["show_save_and_continue"] = True
                extra_context["show_save_and_add_another"] = False
                extra_context["show_save_as_new"] = False
                extra_context["show_publish_button"] = False
                extra_context["show_delete_link"] = self.has_delete_permission(request, obj)
                pending = obj.draft_copies.first()
                if pending is not None:
                    extra_context["pending_draft_pk"] = pending.pk
            elif live_published_pending_draft:
                extra_context["draft_workflow_footer"] = False
                extra_context["show_save"] = True
                extra_context["show_save_and_continue"] = True
                extra_context["show_save_and_add_another"] = False
                extra_context["show_save_as_new"] = False
                extra_context["show_publish_button"] = False
                extra_context["show_delete_link"] = self.has_delete_permission(request, obj)
            elif obj is not None and obj.is_draft_copy:
                extra_context["subtitle"] = f"{obj} ({_('draft')})"
                extra_context["show_save"] = False
                extra_context["show_save_and_add_another"] = False
                extra_context["show_save_as_new"] = False
                extra_context["show_save_and_continue"] = True
                extra_context["show_publish_button"] = True
                extra_context["show_delete_link"] = False
            elif obj is not None and obj.is_live_row and not obj.is_published:
                extra_context["show_save"] = False
                extra_context["show_save_and_add_another"] = False
                extra_context["show_save_as_new"] = False
                extra_context["show_save_and_continue"] = True
                extra_context["show_publish_button"] = True
            elif obj is None:
                extra_context["show_save_and_continue"] = True
                extra_context["show_publish_button"] = False

        return super().change_view(request, object_id, form_url, extra_context=extra_context)
