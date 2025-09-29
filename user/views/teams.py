from django.db.models import Count, Value
from rest_framework import decorators, response, status
from app.utils.mixins.views import BaseModelViewSet
from user.constants import UserRoleChoices
from user.models import User
from user.serializers.teams import TeamMemberSerializer, TeamSerializer


class TeamViewSet(BaseModelViewSet):
    queryset = User.objects.filter(
        user_role=UserRoleChoices.HOST, subordinates__isnull=False
    ).annotate(size=Value(1) + (Count("subordinates")))  # superior + subordinates

    serializer_class = TeamSerializer
    serializers = {
        "get_team_members": TeamMemberSerializer,
        "create_team_member": TeamMemberSerializer,
    }

    @decorators.action(methods=["get"], detail=True, url_path="members")
    def get_team_members(self, request, pk, *args, **kwargs):
        queryset = User.objects.filter(superior=pk)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @get_team_members.mapping.post
    def create_team_member(self, request, pk, *args, **kwargs):
        serializer = self.get_serializer(data={**request.data, "superior": pk})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
