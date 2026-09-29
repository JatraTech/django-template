from backstage.contrib.filters.admin.dropdown_filters import (
    MultipleRelatedDropdownFilter,
    RelatedDropdownFilter,
)
from backstage.contrib.filters.admin.mixins import AutocompleteMixin
from backstage.contrib.filters.forms import AutocompleteDropdownForm


class AutocompleteSelectFilter(AutocompleteMixin, RelatedDropdownFilter):
    form_class = AutocompleteDropdownForm


class AutocompleteSelectMultipleFilter(AutocompleteMixin, MultipleRelatedDropdownFilter):
    form_class = AutocompleteDropdownForm
