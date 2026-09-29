import copy
from typing import Any

from django import forms
from django.db import models

from backstage import widgets

FORMFIELD_OVERRIDES: dict[Any, Any] = {
    models.DateTimeField: {
        "form_class": forms.SplitDateTimeField,
        "widget": widgets.BackstageAdminSplitDateTimeWidget,
    },
    models.DateField: {"widget": widgets.BackstageAdminSingleDateWidget},
    models.TimeField: {"widget": widgets.BackstageAdminSingleTimeWidget},
    models.EmailField: {"widget": widgets.BackstageAdminEmailInputWidget},
    models.CharField: {"widget": widgets.BackstageAdminTextInputWidget},
    models.URLField: {"widget": widgets.BackstageAdminURLInputWidget},
    models.GenericIPAddressField: {"widget": widgets.BackstageAdminTextInputWidget},
    models.UUIDField: {"widget": widgets.BackstageAdminUUIDInputWidget},
    models.TextField: {"widget": widgets.BackstageAdminTextareaWidget},
    models.NullBooleanField: {"widget": widgets.BackstageAdminNullBooleanSelectWidget},
    models.BooleanField: {"widget": widgets.BackstageBooleanSwitchWidget},
    models.IntegerField: {"widget": widgets.BackstageAdminIntegerFieldWidget},
    models.BigIntegerField: {"widget": widgets.BackstageAdminBigIntegerFieldWidget},
    models.DecimalField: {"widget": widgets.BackstageAdminDecimalFieldWidget},
    models.FloatField: {"widget": widgets.BackstageAdminDecimalFieldWidget},
    models.FileField: {"widget": widgets.BackstageAdminFileFieldWidget},
    models.ImageField: {"widget": widgets.BackstageAdminImageFieldWidget},
    models.JSONField: {"widget": widgets.BackstageAdminTextareaWidget},
    models.DurationField: {"widget": widgets.BackstageAdminTextInputWidget},
}

######################################################################
# Postgres
######################################################################
try:
    from django.contrib.postgres.fields import ArrayField, IntegerRangeField
    from django.contrib.postgres.search import SearchVectorField

    FORMFIELD_OVERRIDES.update(
        {
            ArrayField: {"widget": widgets.BackstageAdminTextareaWidget},
            SearchVectorField: {"widget": widgets.BackstageAdminTextareaWidget},
            IntegerRangeField: {"widget": widgets.BackstageAdminIntegerRangeWidget},
        }
    )
except ImportError:  # pragma: no cover
    pass

######################################################################
# Django Money
######################################################################
try:
    from djmoney.models.fields import MoneyField

    FORMFIELD_OVERRIDES.update(
        {
            MoneyField: {"widget": widgets.BackstageAdminMoneyWidget},
        }
    )
except ImportError:  # pragma: no cover
    pass

######################################################################
# Inlines
######################################################################
FORMFIELD_OVERRIDES_INLINE = copy.deepcopy(FORMFIELD_OVERRIDES)

FORMFIELD_OVERRIDES_INLINE.update(
    {
        models.ImageField: {"widget": widgets.BackstageAdminImageSmallFieldWidget},
    }
)
