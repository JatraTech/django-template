import random
import string
import base64

from django.db.models import Q
from rest_framework import serializers

from user.models import User
from django.contrib.auth.tokens import default_token_generator


def generate_username(first_name: str, last_name: str) -> str:
    # Normalize input
    first = first_name.strip().lower()
    last = last_name.strip().lower()

    # Patterns to mix names and numbers
    patterns = [
        f"{first}{last}",
        f"{first}_{last}",
        f"{first}.{last}",
        f"{first[0]}{last}",
        f"{first}{last[0]}",
        f"{last}{first}",
    ]

    # Add random suffix
    base = random.choice(patterns)
    suffix = "".join(random.choices(string.digits, k=3))

    return f"{base}{suffix}"


def get_password_reset_token_for_email_or_username(email_or_username):
    try:
        user = User.objects.get(
            Q(username=email_or_username) | Q(email=email_or_username)
        )
        token = default_token_generator.make_token(user)
        uidb64 = base64.urlsafe_b64encode(str(user.pk).encode()).decode()
        return (user, uidb64, token)
    except User.DoesNotExist:
        raise serializers.ValidationError("Invalid email or username")


def reset_password_for_token(uidb64, token, new_password):
    try:
        uid = base64.urlsafe_b64decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return user
        else:
            raise serializers.ValidationError("Invalid token")
    except (User.DoesNotExist, ValueError, OverflowError, TypeError):
        raise serializers.ValidationError("Invalid token")
