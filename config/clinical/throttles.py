from rest_framework.throttling import SimpleRateThrottle


class APIKeyRateThrottle(SimpleRateThrottle):
    scope = "api_key"

    def get_cache_key(self, request, view):
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            return None
        return f"throttle_{api_key}"
