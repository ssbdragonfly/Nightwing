from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    label = "nightwing_auth"
    name = "nightwing.apps.auth"
