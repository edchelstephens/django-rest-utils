import pytest
import json

from typing import Optional, Any

from django.db.models import QuerySet
from django.test.testcases import SimpleTestCase, TestCase
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate


from logging.logging import TerminalLoggingMixin

from testing.request import (
    DjangoRequestFactoryMixin,
    RestRequestFactoryMixin,
)

User = get_user_model()


class TestMixin(TerminalLoggingMixin):
    """Mixin class for tests."""

    def assertListsAreEqual(
        self, first: list, second: list, msg: Optional[str] = None
    ) -> None:
        """Assert that first and second lists are equal."""

        list_from_first_side_equal = all(
            (
                (item in second) and first.count(item) == second.count(item)
                for item in first
            )
        )

        list_from_second_side_equal = all(
            (
                (item in first) and first.count(item) == second.count(item)
                for item in second
            )
        )

        lists_equal = list_from_first_side_equal and list_from_second_side_equal

        if msg is None:
            msg = "Lists are not equal! \n\n  {} \n\n!= \n \n{}".format(first, second)

        assert lists_equal, msg


@pytest.mark.django_db
@pytest.mark.models
class QuerySetTestMixin:
    """Mixin for query set tests."""

    def assertQuerySetEqualByIds(
        self, first: QuerySet, second: QuerySet, msg: Optional[str] = None
    ) -> None:
        """Assert query set is equal by given"""
        first_queryset_ids = list(first.values_list("id", flat=True))
        second_queryset_ids = list(second.values_list("id", flat=True))

        if msg is None:
            msg = "Queryset ids not equal! {} != {}".format(
                repr(first_queryset_ids), repr(second_queryset_ids)
            )
        assert first_queryset_ids == second_queryset_ids, msg


@pytest.mark.non_db
class NonDBTestCase(TestMixin, SimpleTestCase):
    """Our custom test case wrapper for tests not involving database access."""

    maxDiff = None


@pytest.mark.django_db
@pytest.mark.models
class ModelTestCase(TestMixin, TestCase):
    """Our custom test case wrapper for testing django models."""

    maxDiff = None


@pytest.mark.django_db
@pytest.mark.django_views
class DjangoViewTestCase(TestMixin, DjangoRequestFactoryMixin, TestCase):
    """Our test case wrapper for testing django views."""

    maxDiff = None

    def set_user(self, request, user: User) -> None:
        """Manually set request.user to user.

        To simulate a user logged-in trying to access an endpoint.
        """
        request.user = user

    def get_json_response_data(self, response) -> Any:
        """Get json response data from JSONResponse object content."""
        try:
            return json.loads(response.content)
        except TypeError as exc:
            return json.loads(self.get_string_response(response))
        except Exception as exc:
            raise exc

    def get_dict_response_data(self, response) -> dict:
        """Get expected dictionary response data from deserialized JSONResponse response.content"""
        data = self.get_json_response_data(response)
        if not isinstance(data, dict):
            raise TypeError(
                "deserialized response.content is not a python dict but a {}".format(
                    type(data)
                )
            )
        return data

    def get_list_response_data(self, response) -> list:
        """Get expected list response data from deserialized JSONResponse response.content"""
        data = self.get_json_response_data(response)
        if not isinstance(data, list):
            raise TypeError(
                "deserialized response.content is not a python list but a {}".format(
                    type(data)
                )
            )
        return data

    def get_string_response(self, response) -> str:
        """Get the decoded response string from bytestring response.content"""
        return response.content.decode()


@pytest.mark.django_db
@pytest.mark.api_views
class RestAPITestCase(TestMixin, RestRequestFactoryMixin, APITestCase):
    """Our test case wrapper for rest_framework api views."""

    maxDiff = None

    def set_user(self, request, user: User) -> None:
        """Forcibly set request.user to user.

        This is used on views which requires authenticated requests.
        https://www.django-rest-framework.org/api-guide/testing/#forcing-authentication
        """
        force_authenticate(request, user=user)


class WithRedirectionTestCase(DjangoViewTestCase):
    """Test case for django views with redirections."""

    def run_redirection_assertions(self, response, redirect_url: str) -> None:
        """Run assertions that response is a redirect response object to given redirect url."""

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, redirect_url)


class DjangoJsonListViewTestCase(DjangoViewTestCase):
    """Test case class with helpers for processing views that return JsonResponse of lists of data."""

    def run_list_view_response_data_assertions(
        self, response, expected_data: dict
    ) -> None:
        """Run assertion that response data for a listing endpoint is the same as expected data.

        The endpoint should return a json on this shape:
        {
            "total": <total_count>,
            "records": [],
        }
        """

        response_data = self.get_dict_response_data(response)
        self.assertEqual(response_data["total"], expected_data["total"])
        self.assertListsAreEqual(response_data["records"], expected_data["records"])
