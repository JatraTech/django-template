"""Shared fixtures for django_template tests."""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api():
    return APIClient()
