"""Mixin module for request objects wrappers."""

from django.contrib.auth import get_user_model


User = get_user_model()


class RequestMixin:
    """The base request mixin class."""

    def get_user_id(self, request) -> int:
        """Get request user id."""
        try:
            return request.user.id
        except Exception as exc:
            raise exc
    
    def get_user_instance(self, request) -> User:
        """Get request user instance."""
        try:
            user_id = self.get_user_id(request)
            return User.objects.get(id=user_id)
        except Exception as exc:
            raise exc


class DjangoRequestMixin(RequestMixin):
    """Django HttpRequest object mixin.
    
    https://docs.djangoproject.com/en/3.2/ref/request-response/#httprequest-objects
    """
    pass

class RestRequestMixin(RequestMixin):
    """Django Rest Framework Request object mixin.
    
    https://www.django-rest-framework.org/api-guide/requests/
    """
    
    pass
