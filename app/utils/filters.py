import operator
from collections.abc import Callable
from functools import reduce

from django.db.models import Q
from django_filters import rest_framework as dj_filters
from rest_framework.filters import BaseFilterBackend, SearchFilter as SearchFilter_

from app.utils.mixins.models import NameModelMixin


class BaseModelFilterSet(dj_filters.FilterSet):
    created_at = dj_filters.DateFromToRangeFilter()

    class Meta:
        abstract = True


class SearchFilter(SearchFilter_):
    def get_search_fields(self, view, request):
        fields = super().get_search_fields(view, request) or list()
        fields.append("id")
        fields = set(fields)
        model = None
        if serializer := getattr(view, "serializer_class", None):
            if hasattr(serializer, "Meta") and hasattr(
                serializer.Meta,
                "model",
            ):
                model = serializer.Meta.model
                if issubclass(model, NameModelMixin):
                    fields = fields.union(["name"])
        if field_from_querystring := request.query_params.get("search_fields"):
            fields = fields.union([search_field.strip() for search_field in field_from_querystring.split(",")])
        return fields


class AudienceFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        if (
            not view.authentication_classes
        ):  # if view doesn't have auth enforced, no need to check for audience. the view is open for all
            return queryset
        # if the user role is found in the audience_lookups of the view, filter the queryset accordingly
        if hasattr(view, "audience_lookups") and user.user_role in view.audience_lookups:
            if isinstance(view.audience_lookups[user.user_role], Callable):
                "if the entry is a function, preferably lambda function. i.e. lambda user: Q(created_by=user), pass user as the first param"
                return queryset.filter(view.audience_lookups[user.user_role](user))
            return queryset.filter(**{view.audience_lookups[user.user_role]: user})
        return queryset


class ExtendedSearchFilter(SearchFilter):
    """
    Custom SearchFilter that applies default DRF search_fields filtering,
    then ORs additional conditions for selected fields.
    """

    extra_search_fields = []  # override this in the view

    def filter_queryset(self, request, queryset, view):
        # Let DRF apply its normal filtering
        queryset = super().filter_queryset(request, queryset, view)

        search_terms = self.get_search_terms(request)
        extra_fields = getattr(view, "extra_search_fields", self.extra_search_fields)

        if not search_terms or not extra_fields:
            return queryset

        # Build OR filter across selected extra fields & search terms
        or_filter = reduce(
            operator.or_,
            (
                reduce(operator.or_, (Q(**{f"{field}__icontains": term}) for field in extra_fields))
                for term in search_terms
            ),
        )

        # Combine results with OR so you include matches from extra fields
        return (queryset | view.queryset.filter(or_filter)).distinct()
