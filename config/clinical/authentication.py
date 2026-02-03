from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ClinicalAPIKey


class APIKeyAuthentication(BaseAuthentication):
    """
    Header:
    X-API-KEY: your_api_key_here
    """

    def authenticate(self, request):
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            raise AuthenticationFailed("API key required")

        try:
            key_obj = ClinicalAPIKey.objects.get(
                key=api_key,
                is_active=True
            )
        except ClinicalAPIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive API key")

        return (None, None)
