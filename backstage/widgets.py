import json
from collections.abc import Callable
from typing import Any

from django import forms
from django.conf import settings
from django.contrib.admin.options import VERTICAL
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.widgets import (
    AdminBigIntegerFieldWidget,
    AdminDateWidget,
    AdminEmailInputWidget,
    AdminFileWidget,
    AdminIntegerFieldWidget,
    AdminRadioSelect,
    AdminSplitDateTime,
    AdminTextareaWidget,
    AdminTextInputWidget,
    AdminTimeWidget,
    AdminURLFieldWidget,
    AdminUUIDInputWidget,
    ForeignKeyRawIdWidget,
    RelatedFieldWidgetWrapper,
)
from django.db.models import ManyToOneRel
from django.forms import (
    CheckboxInput,
    CheckboxSelectMultiple,
    ClearableFileInput,
    MultiWidget,
    NullBooleanSelect,
    NumberInput,
    PasswordInput,
    Select,
    SelectMultiple,
)
from django.forms.widgets import Input
from django.utils.translation import gettext_lazy as _

from backstage.exceptions import BackstageException

BUTTON_CLASSES = [
    "backstage-control",
    "border",
    "box-border",
    "cursor-pointer",
    "font-medium",
    "inline-flex",
    "items-center",
    "justify-center",
    "min-h-9",
    "appearance-none",
    "px-3",
    "py-1.5",
    "rounded-default",
    "text-center",
    "whitespace-nowrap",
    "bg-primary-600",
    "border-transparent",
    "text-white",
]

LABEL_CLASSES = [
    "block",
    "font-semibold",
    "mb-2",
    "text-font-important-light",
    "text-sm",
    "dark:text-font-important-dark",
]

CHECKBOX_LABEL_CLASSES = [
    "font-semibold",
    "ml-2",
    "text-sm",
    "text-font-important-light",
    "dark:text-font-important-dark",
]

BASE_CLASSES = [
    "border",
    "border-border",
    "bg-background",
    "font-medium",
    "min-w-20",
    "placeholder-base-400",
    "rounded-default",
    "transition-colors",
    "text-font-default-light",
    "text-sm",
    "focus-visible:outline-none",
    "group-[.errors]:border-red-600",
    "dark:bg-[var(--input-background)]",
    "dark:border-border",
    "dark:text-font-default-dark",
    "dark:group-[.errors]:border-red-500",
    "dark:scheme-dark",
    "group-[.primary]:border-transparent",
    "disabled:!bg-muted",
    "dark:disabled:!bg-base-800",
]

BASE_INPUT_CLASSES = [
    *BASE_CLASSES,
    "px-3",
    "py-2",
    "w-full",
]

INPUT_CLASSES = [*BASE_INPUT_CLASSES, "max-w-2xl"]

DATETIME_CLASSES = [*BASE_INPUT_CLASSES, "min-w-52"]

COLOR_CLASSES = [*BASE_CLASSES, "h-[38px]", "px-2", "py-2", "w-32"]

INPUT_CLASSES_READONLY = [*BASE_INPUT_CLASSES]

TEXTAREA_CLASSES = [
    *BASE_INPUT_CLASSES,
    "max-w-4xl",
    "appearance-none",
]

TEXTAREA_EXPANDABLE_CLASSES = [
    "block",
    "field-sizing-content",
    "min-h-[38px]",
    "!max-w-2xl",
]

SELECT_CLASSES = [
    *BASE_INPUT_CLASSES,
    "pr-8!",
    "max-w-2xl",
    "appearance-none",
    "text-ellipsis",
]

PROSE_CLASSES = [
    "font-normal",
    "whitespace-normal",
    "prose-sm",
    "prose-a:text-link",
    "prose-blockquote:border-l-4",
    "prose-blockquote:not-italic",
    "prose-pre:bg-base-50",
    "prose-pre:rounded-default",
    "prose-headings:font-semibold",
    "prose-headings:text-important",
    "prose-headings:tracking-tight",
    "prose-strong:font-semibold",
    "prose-ol:list-decimal",
    "prose-ol:flex",
    "prose-ol:flex-col",
    "prose-ol:gap-0.5",
    "prose-ol:mt-2",
    "prose-ul:list-disc",
    "prose-ul:flex",
    "prose-ul:flex-col",
    "prose-ul:gap-0.5",
    "prose-ul:mt-2",
    "prose-li:m-0",
    "dark:prose-pre:bg-base-800",
    "dark:prose-blockquote:border-border",
    "dark:prose-blockquote:text-base-300",
]

CHECKBOX_CLASSES = [
    "appearance-none",
    "bg-white",
    "block",
    "border",
    "border-border",
    "h-4",
    "min-w-4",
    "relative",
    "rounded-[4px]",
    "w-4",
    "dark:bg-[var(--input-background)]",
    "dark:border-border",
    "dark:checked:after:text-white",
    "after:absolute",
    r"after:content-['check\_small']",
    "after:flex!",
    "after:h-4",
    "after:items-center",
    "after:justify-center",
    "after:leading-none",
    "after:material-symbols-outlined",
    "after:-ml-px",
    "after:-mt-px",
    "after:text-white",
    "after:w-4",
    "dark:after:text-transparent",
    "checked:bg-primary-600",
    "dark:checked:bg-primary-600",
    "checked:border-primary-600",
    "dark:checked:border-primary-600",
]

RADIO_CLASSES = [
    "appearance-none",
    "bg-white",
    "block",
    "border",
    "border-border",
    "h-4",
    "min-w-4",
    "relative",
    "rounded-full",
    "w-4",
    "dark:bg-[var(--input-background)]",
    "dark:border-border",
    "after:absolute",
    "after:bg-transparent",
    "after:content-['']",
    "after:flex",
    "after:h-2",
    "after:items-center",
    "after:justify-center",
    "after:leading-none",
    "after:left-1/2",
    "after:rounded-full",
    "after:text-white",
    "after:top-1/2",
    "after:-translate-x-1/2",
    "after:-translate-y-1/2",
    "after:w-2",
    "dark:after:text-base-700",
    "dark:after:bg-transparent",
    "checked:bg-primary-600",
    "checked:border-primary-600",
    "checked:after:bg-white",
    "dark:checked:after:bg-base-900",
]

SWITCH_CLASSES = [
    "appearance-none",
    "bg-base-300",
    "block",
    "cursor-pointer",
    "h-5",
    "relative",
    "rounded-full",
    "w-8",
    "min-w-8",
    "disabled:cursor-not-allowed",
    "disabled:opacity-50",
    "focus:outline-none",
    "after:absolute",
    "after:bg-white",
    "after:content-['']",
    "after:bg-red-300",
    "after:h-3",
    "after:rounded-full",
    "after:transition-all",
    "after:left-1",
    "after:top-1",
    "after:w-3",
    "checked:bg-green-500",
    "checked:after:left-4",
    "dark:bg-base-600",
    "dark:checked:bg-green-700",
]

FILE_CLASSES = [
    "bg-background",
    "border",
    "border-border",
    "flex",
    "grow",
    "items-center",
    "overflow-hidden",
    "rounded-default",
    "max-w-2xl",
    "focus-within:outline-2",
    "focus-within:-outline-offset-2",
    "focus-within:outline-primary-600",
    "group-[.errors]:border-red-600",
    "focus-within:group-[.errors]:outline-red-500",
    "dark:bg-[var(--input-background)]",
    "dark:border-border",
    "dark:group-[.errors]:border-red-500",
    "dark:focus-within:group-[.errors]:outline-red-500",
]


class BackstagePrefixSuffixMixin(Input):
    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        widget = context["widget"]

        if "prefix" in self.attrs:
            widget["prefix"] = self.attrs["prefix"]
            del self.attrs["prefix"]

        if "prefix_icon" in self.attrs:
            widget["prefix_icon"] = self.attrs["prefix_icon"]
            self.attrs["class"] = " ".join([self.attrs["class"], "pl-9"])
            del self.attrs["prefix_icon"]

        if "suffix" in self.attrs:
            widget["suffix"] = self.attrs["suffix"]
            del self.attrs["suffix"]

        if "suffix_icon" in self.attrs:
            widget["suffix_icon"] = self.attrs["suffix_icon"]
            self.attrs["class"] = " ".join([self.attrs["class"], "pr-9"])
            del self.attrs["suffix_icon"]

        widget.update(
            {
                "name": name,
                "is_hidden": self.is_hidden,
                "required": self.is_required,
                "value": self.format_value(value),
                "attrs": self.build_attrs(self.attrs, attrs),
                "template_name": self.template_name,
            }
        )

        return {
            "widget": widget,
        }


class BackstageAdminTextInputWidget(BackstagePrefixSuffixMixin, AdminTextInputWidget):
    template_name = "backstage/widgets/text.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]),
            }
        )


class BackstageAdminURLInputWidget(AdminURLFieldWidget):
    template_name = "backstage/widgets/url.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]),
            }
        )


class BackstageAdminColorInputWidget(AdminTextInputWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "type": "color",
                "class": " ".join([*COLOR_CLASSES, attrs.get("class", "") if attrs else ""]),
            }
        )


class BackstageAdminUUIDInputWidget(AdminUUIDInputWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]),
            }
        )


class BackstageAdminIntegerRangeWidget(MultiWidget):
    template_name = "backstage/widgets/range.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        attrs = attrs or {}

        attrs["class"] = " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""])

        _widgets = (NumberInput(attrs=attrs), NumberInput(attrs=attrs))

        super().__init__(_widgets, attrs)

    def decompress(self, value: str | None) -> tuple[Callable | None, ...]:
        return (value.lower, value.upper) if value else (None, None)


class BackstageAdminEmailInputWidget(AdminEmailInputWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]),
            }
        )


class FileFieldMixin(ClearableFileInput):
    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        widget = super().get_context(name, value, attrs)

        widget["widget"].update(
            {
                "class": " ".join([*CHECKBOX_CLASSES, *["form-check-input"]]),
                "file_wrapper_class": " ".join(FILE_CLASSES),
                "file_input_class": " ".join(
                    [
                        self.attrs.get("class", ""),
                        *[
                            "opacity-0",
                            "pointer-events-none",
                        ],
                    ]
                ),
            }
        )

        return widget


class BackstageAdminImageFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "backstage/widgets/clearable_file_input.html"


class BackstageAdminFileFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "backstage/widgets/clearable_file_input_small.html"


class BackstageAdminImageSmallFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "backstage/widgets/clearable_file_input_small.html"


class BackstageAdminDateWidget(AdminDateWidget):
    template_name = "backstage/widgets/date.html"

    def __init__(self, attrs: dict[str, Any] | None = None, format: str | None = None) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vDateField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "10",
        }
        super().__init__(attrs=attrs, format=format)

    class Media:
        js = [
            "admin/js/core.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]


class BackstageAdminSingleDateWidget(AdminDateWidget):
    template_name = "backstage/widgets/date.html"

    def __init__(self, attrs: dict[str, Any] | None = None, format: str | None = None) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vDateField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "10",
        }
        super().__init__(attrs=attrs, format=format)


class BackstageAdminTimeWidget(AdminTimeWidget):
    template_name = "backstage/widgets/time.html"

    def __init__(self, attrs: dict[str, Any] | None = None, format: str | None = None) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vTimeField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "8",
        }
        super().__init__(attrs=attrs, format=format)

    class Media:
        js = [
            "admin/js/core.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]


class BackstageAdminSingleTimeWidget(AdminTimeWidget):
    template_name = "backstage/widgets/time.html"

    def __init__(self, attrs: dict[str, Any] | None = None, format: str | None = None) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vTimeField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "8",
        }
        super().__init__(attrs=attrs, format=format)


class BackstageAdminTextareaWidget(AdminTextareaWidget):
    template_name = "backstage/widgets/textarea.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        attrs = attrs or {}

        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [
                        "vLargeTextField",
                        *TEXTAREA_CLASSES,
                        attrs.get("class", "") if attrs else "",
                    ]
                ),
            }
        )


class BackstageAdminExpandableTextareaWidget(BackstageAdminTextareaWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        attrs = attrs or {}

        attrs.update({"rows": 2})

        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [
                        "vLargeTextField",
                        *TEXTAREA_CLASSES,
                        *TEXTAREA_EXPANDABLE_CLASSES,
                        attrs.get("class", "") if attrs else "",
                    ]
                ),
            }
        )


class BackstageAdminSplitDateTimeWidget(AdminSplitDateTime):
    template_name = "backstage/widgets/split_datetime.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        widgets = [
            BackstageAdminDateWidget(attrs={"placeholder": _("Date")}),
            BackstageAdminTimeWidget(attrs={"placeholder": _("Time")}),
        ]
        MultiWidget.__init__(self, widgets, attrs)

    class Media:
        js = [
            "admin/js/core.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]


class BackstageAdminSplitDateTimeVerticalWidget(AdminSplitDateTime):
    template_name = "backstage/widgets/split_datetime_vertical.html"

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        date_attrs: dict[str, Any] | None = None,
        time_attrs: dict[str, Any] | None = None,
        date_label: str | None = None,
        time_label: str | None = None,
    ) -> None:
        self.date_label = date_label
        self.time_label = time_label

        widgets = [
            BackstageAdminDateWidget(attrs=date_attrs),
            BackstageAdminTimeWidget(attrs=time_attrs),
        ]
        MultiWidget.__init__(self, widgets, attrs)

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)

        if self.date_label is not None:
            context["date_label"] = self.date_label
        else:
            context["date_label"] = _("Date")

        if self.time_label is not None:
            context["time_label"] = self.time_label
        else:
            context["time_label"] = _("Time")

        return context


class BackstageAdminIntegerFieldWidget(AdminIntegerFieldWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]),
            }
        )


class BackstageAdminDecimalFieldWidget(AdminIntegerFieldWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]),
            }
        )


class BackstageAdminBigIntegerFieldWidget(AdminBigIntegerFieldWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]),
            }
        )


class BackstageAdminNullBooleanSelectWidget(NullBooleanSelect):
    template_name = "backstage/widgets/select.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        attrs = attrs or {}

        attrs["class"] = " ".join([*SELECT_CLASSES, attrs.get("class", "") if attrs else ""])
        super().__init__(attrs)


class BackstageAdminSelectWidget(Select):
    template_name = "backstage/widgets/select.html"

    def __init__(self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()) -> None:
        attrs = attrs or {}

        attrs["class"] = " ".join([*SELECT_CLASSES, attrs.get("class", "") if attrs else ""])
        super().__init__(attrs, choices)


class BackstageAdminSelect2Widget(Select):
    def __init__(self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()) -> None:
        attrs = attrs or {}

        attrs["data-theme"] = "admin-autocomplete"
        attrs["class"] = " ".join(["backstage-admin-autocomplete", attrs.get("class", "") if attrs else ""])

        super().__init__(attrs, choices)

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "backstage/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class BackstageAdminSelectMultipleWidget(SelectMultiple):
    def __init__(self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()) -> None:
        attrs = attrs or {}

        attrs["class"] = " ".join([*SELECT_CLASSES, attrs.get("class", "") if attrs else ""])
        super().__init__(attrs, choices)


class BackstageAdminSelect2MultipleWidget(SelectMultiple):
    def __init__(self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()) -> None:
        attrs = attrs or {}

        attrs["data-theme"] = "admin-autocomplete"
        attrs["class"] = " ".join(
            [
                "backstage-admin-autocomplete admin-autocomplete",
                attrs.get("class", "") if attrs else "",
            ]
        )

        super().__init__(attrs, choices)

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "backstage/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class BackstageAdminRadioSelectWidget(AdminRadioSelect):
    template_name = "backstage/widgets/radio.html"
    option_template_name = "backstage/widgets/radio_option.html"

    def __init__(self, radio_style: int | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if radio_style is None:
            radio_style = VERTICAL

        self.radio_style = radio_style
        self.attrs["class"] = " ".join([*RADIO_CLASSES, self.attrs.get("class", "")])

    def get_context(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context(*args, **kwargs)
        context.update({"radio_style": self.radio_style})
        return context


class AccentPaletteRadioWidget(BackstageAdminRadioSelectWidget):
    template_name = "backstage/widgets/accent_palette_radio.html"
    option_template_name = "backstage/widgets/accent_palette_option.html"

    def create_option(
        self,
        name: str,
        value: str,
        label: str,
        selected: bool,
        index: int,
        subindex: int | None = None,
        attrs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            from backstage.accent_palettes import get_accent_palette

            option["swatch_color"] = get_accent_palette(str(value))["preview_hex"]
            option_attrs = option.setdefault("attrs", {})
            option_attrs["class"] = " ".join(filter(None, [option_attrs.get("class", ""), "sr-only"]))
        return option


class BackstageAdminCheckboxSelectMultipleWidget(CheckboxSelectMultiple):
    template_name = "backstage/widgets/radio.html"
    option_template_name = "backstage/widgets/radio_option.html"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.attrs = {"class": " ".join([*CHECKBOX_CLASSES, self.attrs.get("class", "") if self.attrs else ""])}


class BackstageBooleanWidget(CheckboxInput):
    def __init__(self, attrs: dict[str, Any] | None = None, check_test: Callable | None = None) -> None:
        attrs = attrs or {}

        super().__init__(
            {
                **(attrs or {}),
                "class": " ".join([*CHECKBOX_CLASSES, attrs.get("class", "") if attrs else ""]),
            },
            check_test,
        )


class BackstageBooleanSwitchWidget(CheckboxInput):
    def __init__(self, attrs: dict[str, Any] | None = None, check_test: Callable | None = None) -> None:
        attrs = attrs or {}

        super().__init__(
            {
                **(attrs or {}),
                "class": " ".join([*SWITCH_CLASSES, attrs.get("class", "") if attrs else ""]),
            },
            check_test,
        )


class BackstageForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    template_name = "backstage/widgets/foreign_key_raw_id.html"

    def __init__(
        self,
        rel: ManyToOneRel,
        admin_site: AdminSite,
        attrs: dict[str, Any] | None = None,
        using: Any | None = None,
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vForeignKeyRawIdAdminField",
                    *INPUT_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
        }
        super().__init__(rel, admin_site, attrs, using)


class BackstageAdminPasswordWidget(PasswordInput):
    def __init__(self, attrs: dict[str, Any] | None = None, render_value: bool = False) -> None:
        super().__init__(
            {
                **(attrs or {}),
                "class": " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]),
            },
            render_value,
        )


class BackstageAdminPasswordToggleWidget(BackstageAdminPasswordWidget):
    template_name = "backstage/widgets/password_toggle.html"


class AutocompleteWidgetMixin:
    is_required: bool

    def __init__(self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()) -> None:
        attrs = attrs or {}

        attrs.update(
            {
                "data-ajax--cache": "true",
                "data-ajax--delay": 250,
                "data-ajax--type": "GET",
                "data-theme": "admin-autocomplete",
                "data-allow-clear": json.dumps(not self.is_required),
                "data-placeholder": "",
                "class": " ".join(
                    [
                        "backstage-admin-autocomplete admin-autocomplete",
                        attrs.get("class", "") if attrs else "",
                    ]
                ),
            }
        )
        super().__init__(attrs, choices)

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "backstage/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class BackstageAdminAutocompleteWidget(AutocompleteWidgetMixin, Select):
    option_template_name = "backstage/widgets/select_option_autocomplete.html"


class BackstageAdminAutocompleteModelChoiceFieldWidget(AutocompleteWidgetMixin, Select):
    option_template_name = "backstage/widgets/select_option_modelchoicefield_autocomplete.html"


class BackstageAdminMultipleAutocompleteWidget(AutocompleteWidgetMixin, SelectMultiple):
    option_template_name = "backstage/widgets/select_option_autocomplete.html"


class BackstageAdminMultipleAutocompleteModelChoiceFieldWidget(AutocompleteWidgetMixin, SelectMultiple):
    option_template_name = "backstage/widgets/select_option_modelchoicefield_autocomplete.html"


class BackstageAdminRelatedFieldWrapperWidget(RelatedFieldWidgetWrapper):
    template_name = "backstage/widgets/related_widget_wrapper.html"


try:
    from djmoney.forms.widgets import MoneyWidget
    from djmoney.settings import CURRENCY_CHOICES

    class BackstageAdminMoneyWidget(MoneyWidget):
        template_name = "backstage/widgets/split_money.html"

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            attrs = {}

            if "attrs" in kwargs:
                attrs = kwargs.pop("attrs")

            super().__init__(
                amount_widget=BackstageAdminTextInputWidget(attrs=attrs),
                currency_widget=BackstageAdminSelectWidget(
                    choices=CURRENCY_CHOICES,
                    attrs={
                        "aria-label": _("Select currency"),
                    },
                ),
            )

except ImportError:

    class BackstageAdminMoneyWidget(forms.Widget):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise BackstageException("django-money not installed")


try:
    from location_field.widgets import LocationWidget

    class BackstageAdminLocationWidget(LocationWidget):
        def __init__(self, attrs: dict[str, Any] | None = None, **kwargs: Any) -> None:
            based_fields = kwargs.pop("based_fields", [])
            super().__init__(
                attrs={
                    **(attrs or {}),
                    "class": " ".join([*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]),
                },
                based_fields=based_fields,
                **kwargs,
            )
except ImportError:

    class BackstageAdminLocationWidget:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise BackstageException("django-location-field not installed")
