from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse, resolve
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class JWTAuthenticationMiddleware:
    EXCLUDED_ENDPOINTS = ["home", "login", "register", "api-login", "api-register"]
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            resolved = resolve(request.path_info)
            if resolved.url_name in self.EXCLUDED_ENDPOINTS:
                response = self.get_response(request)
            else:
                auth = JWTAuthentication()
                auth_result = auth.authenticate(request)
                if auth_result is not None:
                    user, _ = auth_result  # Extract user from JWT
                    request.user = user  # Set request.user
        except AuthenticationFailed:
            pass
        response = self.get_response(request)
        return response
