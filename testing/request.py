from django.test import RequestFactory

from rest_framework.test import APIRequestFactory

from testing.session import SessionRequiredTestMixin


class RequestFactoryMixin:
    """Mixin for request factories.."""

    REQUEST_FACTORY = RequestFactory

    def get_request_factory(self):
        """Get request factory instance."""
        return self.REQUEST_FACTORY()


class DjangoRequestFactoryMixin(RequestFactoryMixin, SessionRequiredTestMixin):
    """Django view request factory
    
    https://docs.djangoproject.com/en/3.1/topics/testing/advanced/#django.test.RequestFactory
    """

    REQUEST_FACTORY = RequestFactory


class RestRequestFactoryMixin(RequestFactoryMixin, SessionRequiredTestMixin):
    """Rest Framework's API view request factory.
    
    https://www.django-rest-framework.org/api-guide/testing/#apirequestfactory
    """

    REQUEST_FACTORY = APIRequestFactory

    def get_enforced_csrf_api_request_factory(self):
        """Return an instance of APIRequestFactory with csrf checks enforced."""
        return self.REQUEST_FACTORY(enforce_csrf_checks=True)