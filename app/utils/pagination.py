from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
from rest_framework import response


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class DummyPagination(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        return queryset

    def get_paginated_response(self, data):
        return response.Response(
            OrderedDict(
                [
                    ("count", len(data)),
                    ("next", None),
                    ("previous", None),
                    ("results", data),
                ]
            )
        )
