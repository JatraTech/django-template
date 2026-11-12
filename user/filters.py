from django_filters import rest_framework as filters

from django_jt.filters import BaseModelFilterSet
from user.models import User


class UserFilterSet(BaseModelFilterSet):
    user_role = filters.CharFilter()
    username = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["user_role", "username"]
