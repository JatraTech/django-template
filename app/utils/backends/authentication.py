from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model, login
from django.db.models.base import Model
from app.utils.mixins.models.constants import ActivityStatusChoices
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class StatusBackend(ModelBackend):
    # def authenticate(self, request, username=None, password=None):
    #     try:
    #         user = User.objects.get(username=username)
    #         if (
    #             user.check_password(password)
    #             and user.status == ActivityStatusChoices.ACTIVE
    #         ):
    #             return user
    #         return None
    #     except User.DoesNotExist:
    #         return None
    pass
