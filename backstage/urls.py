from django.urls import path

from backstage.views import theme_css_view

urlpatterns = [
    path("theme.css", theme_css_view, name="backstage-theme-css"),
]
