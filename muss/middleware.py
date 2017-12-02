from django.conf import settings
from django.contrib.auth.middleware import get_user
from django.core.cache import cache
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class ActiveUserMiddleware(MiddlewareMixin):
    """
    Set user authenticate.
    """
    def process_request(self, request):
        current_user = request.user
        if request.user.is_authenticated:
            now = timezone.now()
            cache.set(
                'seen_%s' % (current_user.username), now,
                settings.USER_LASTSEEN_TIMEOUT
            )


class RestrictStaffToAdminMiddleware(MiddlewareMixin):
    """
    A middleware that restricts staff members access to administration panels.
    """
    def process_request(self, request):
        if request.path.startswith(reverse('admin:index')):
            if request.user.is_authenticated:
                if not request.user.is_staff:
                    raise Http404
            else:
                raise Http404


class AuthenticationMiddlewareJWT(MiddlewareMixin):
    """
    Middleware for auth django and jwt
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = SimpleLazyObject(
            lambda: self.__class__.get_jwt_user(request)
        )
        return self.get_response(request)

    @staticmethod
    def get_jwt_user(request):
        user = get_user(request)
        if user.is_authenticated:
            return user
        jwt_authentication = JSONWebTokenAuthentication()
        if jwt_authentication.get_jwt_value(request):
            user, jwt = jwt_authentication.authenticate(request)
        return user
