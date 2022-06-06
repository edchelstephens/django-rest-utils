from typing import Any, Optional

from django.contrib.sessions.middleware import SessionMiddleware

class SessionTestMixin:
    """Session Test mixin."""

    def is_session_empty(self, request) -> int:
        """Check if request.session is empty."""
        return len(request.session.values()) == 0

    def assertSessionEmpty(self, request, msg: Optional[str] = None) -> None:
        """Assert that request.session does not contain any values."""

        if msg is None:
            msg = "request.session contains values. request.session.values() == {}".format(
                request.session.values()
            )

        assert self.is_session_empty(request), msg

    def assertSessionNotEmpty(self, request, msg: Optional[str] = None) -> None:
        """Assert that request.session contains at least one key value pair."""

        if msg is None:
            msg = "request.session has no key value pairs. request.session.values() == {}".format(
                request.session.values()
            )

        assert not self.is_session_empty(request), msg


class SessionRequiredTestMixin(SessionTestMixin):
    """Mixin for tests with request.session requirements."""

    def add_session(self, request) -> None:
        """Add session object to request by using SessionMiddleware."""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    def set_session_value(self, request, key: str, value: Any) -> None:
        """Set key value on request.session"""
        request.session[key] = value

    def set_session_values(self, request, **kwargs) -> None:
        """Set key values in form of keyword arguments on request.session"""
        request.session.update(kwargs)

 