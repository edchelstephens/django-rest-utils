from exceptions import HumanReadableError
from views.view import DjangoViewAPIMixin

from testing.testcases import NonDBTestCase, DjangoViewTestCase


class DjangoViewAPIMixinTest(NonDBTestCase):
    """DjangoViewAPIMixin tests."""

    def setUp(self) -> None:
        """Run this setUp before each test."""
        super().setUp()
        self.mixin = DjangoViewAPIMixin()
        self.valid_error_dict = {
            "title": "Error",
            "message": "Unable to process request.",
        }
        self.invalid_error_dict = {
            "title": None,
            "message": None,
        }
        self.information_status = 100
        self.success_status_200 = 200
        self.redirection_status_301 = 301
        self.client_error_status_400 = 400
        self.server_error_status_500 = 500
        self.non_error_codes = [
            self.information_status,
            self.success_status_200,
            self.redirection_status_301,
        ]
        self.human_readable_error = HumanReadableError("Incorrect data")
        self.exception_error = Exception("Error")
        self.xml_content_type = "application/xml"
        self.json_content_type = "application/xml"

    def test_raise_error_raises_human_readable_error_sets_error_dict_and_error_status(
        self,
    ) -> None:
        """raise_error() raises a HumanReadableError sets error dict and error status."""
        title = "Forbidden."
        message = "Unauthorized."
        status = 403
        errors = ["Not enough priveleges."]
        with self.assertRaises(HumanReadableError):
            self.mixin.raise_error(
                title=title, message=message, status=status, errors=errors
            )
        self.assertEqual(self.mixin.error_dict["title"], title)
        self.assertEqual(self.mixin.error_dict["message"], message)
        self.assertEqual(self.mixin.error_dict["errors"], errors)
        self.assertEqual(self.mixin.status, status)

    def test_stopper(
        self,
    ) -> None:
        """stopper() method raises a HumanReadableError and sets testing title and message."""

        with self.assertRaises(HumanReadableError):
            self.mixin.stopper()

        self.assertEqual(self.mixin.error_dict["title"], "Testing")
        self.assertEqual(self.mixin.error_dict["message"], "Stopper")
        self.assertEqual(self.mixin.status, 400)


class DjangoViewAPIMixinQueryMethodsTest(DjangoViewAPIMixinTest):
    """DjangoViewAPIMixin tests on query methods which returns booleans."""

    def setUp(self) -> None:
        """Run this setUp before each test."""
        super().setUp()

    def test_is_valid_error_dict_on_valid(self) -> None:
        """is_valid_error_dict() returns True on valid error dict."""
        self.assertTrue(self.mixin.is_valid_error_dict(self.valid_error_dict))

    def test_is_valid_error_dict_on_invalid(self) -> None:
        """is_valid_error_dict() returns False on invalid error dict."""
        self.assertFalse(self.mixin.is_valid_error_dict(self.invalid_error_dict))

    def test_is_valid_error_code_on_400(self) -> None:
        """is_valid_error_code() returns True on 400"""
        self.assertTrue(self.mixin.is_valid_error_code(self.client_error_status_400))

    def test_is_valid_error_code_on_500(self) -> None:
        """is_valid_error_code() returns True on 500"""
        self.assertTrue(self.mixin.is_valid_error_code(self.server_error_status_500))

    def test_is_valid_error_code_on_non_error_status_returns_False(self) -> None:
        """is_valid_error_code() returns False on non client or server response error status codes."""

        is_valid_error_codes = all(
            [self.mixin.is_valid_error_code(code) for code in self.non_error_codes]
        )

        self.assertFalse(is_valid_error_codes)

    def test_is_error_human_readable_on_human_readable_error(self) -> None:
        """is_error_human_readable() returns True on instance of HumanReadableError"""
        self.assertTrue(self.mixin.is_error_human_readable(self.human_readable_error))

    def test_is_error_human_readable_on_non_human_readable_error(self) -> None:
        """is_error_human_readable() returns False on non instance of HumanReadableError"""
        self.assertFalse(self.mixin.is_error_human_readable(self.exception_error))


class DjangoViewAPIMixinResponseMethodsTest(DjangoViewAPIMixinTest, DjangoViewTestCase):
    """DjangoViewTestCase for methods that returns responses."""

    def setUp(self) -> None:
        """Run this setUp before each test."""
        super().setUp()

    def test_success_response_returns_success_http_response(self) -> None:
        """success_response() returns a success http response."""
        data = {"title": "Success", "message": "Record saved."}
        status = 201
        response = self.mixin.success_response(data=data, status=status)
        response_data = self.get_dict_response_data(response)

        self.assertEqual(response.status_code, status)
        self.assertEqual(response_data, data)

    def test_success_response_sets_correct_status_by_default(self) -> None:
        """success_response() sets correct status and returns a success http response."""
        data = {"title": "Success", "message": "Record saved."}
        status = 701
        response = self.mixin.success_response(data=data, status=status)
        response_data = self.get_dict_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, data)

    def test_error_response_returns_error_http_response(self) -> None:
        """error_response() returns a error http response."""
        data = {"title": "Forbidden", "message": "Unauthorized."}
        status = 403
        response = self.mixin.error_response(
            exception=self.exception_error, error_data=data, status=status
        )
        response_data = self.get_dict_response_data(response)

        self.assertEqual(response.status_code, status)
        self.assertEqual(response_data, data)

    def test_error_response_returns_default_response_when_specific_parameters_are_not_provided(
        self,
    ) -> None:
        """error_response() returns default error http response when specific parameters are not provided"""
        self.mixin.error_dict = self.mixin.get_default_error_dict()
        response = self.mixin.error_response(exception=self.exception_error)
        response_data = self.get_dict_response_data(response)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data, self.mixin.get_default_error_dict())

    def test_server_error_response_returns_server_error_response_data(
        self,
    ) -> None:
        """server_error_response() returns server error response data"""
        title = "Server unavailable"
        message = "The server is not ready to handle the request for now."
        status = 503

        response = self.mixin.server_error_response(
            exception=self.exception_error,
            title=title,
            message=message,
            status=status,
        )
        response_data = self.get_dict_response_data(response)

        self.assertEqual(response.status_code, status)
        self.assertEqual(response_data["title"], title)
        self.assertEqual(response_data["message"], message)

    def test_server_error_response_returns_default_response_when_specific_parameters_are_not_provided(
        self,
    ) -> None:
        """server_error_response() returns default server error http response when specific parameters are not provided"""
        response = self.mixin.server_error_response(exception=self.exception_error)
        response_data = self.get_dict_response_data(response)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_data["title"], "Server Error")
        self.assertEqual(response_data["message"], "Please contact developer.")


class DjangoViewAPIMixinGetterMethodsTest(DjangoViewAPIMixinTest):
    """DjangoViewAPIMixinTest getter methods test."""

    def setUp(self) -> None:
        """Run this setUp before each test."""
        super().setUp()

    def test_get_content_type_returns_valid_passed_content_type(self) -> None:
        """get_content_type() returns valid passed content type."""
        self.assertEqual(
            self.mixin.get_content_type(self.xml_content_type), self.xml_content_type
        )

    def test_get_content_type_returns_default_content_returns_default_mixin_content_type_when_non_passed(
        self,
    ) -> None:
        """get_content_type() default mixin content type."""
        self.assertEqual(self.mixin.get_content_type(), self.mixin.CONTENT_TYPE)

    def test_get_error_data_on_human_readable_error_returns_correct_error_data(
        self,
    ) -> None:
        """get_error_data() gets correct error data."""
        error_data = self.mixin.get_error_data(
            self.human_readable_error, self.invalid_error_dict
        )
        self.assertEqual(error_data["title"], "Error")
        self.assertEqual(error_data["message"], str(self.human_readable_error))

    def test_get_error_data_returns_default_error_dict_on_error_data_not_conforming_to_standard_error_dict(
        self,
    ) -> None:
        """get_error_data() gets correct error data."""

        error_data = self.mixin.get_error_data(
            self.exception_error, self.invalid_error_dict
        )
        self.assertEqual(error_data["title"], "Error")
        self.assertEqual(error_data["message"], "Unable to process request.")

    def test_get_default_error_dict(self) -> None:
        """get_default_error_dict() returns expected data."""

        expected = {
            "title": "Error",
            "message": "Unable to process request.",
            "errors": None,
        }

        self.assertEqual(self.mixin.get_default_error_dict(), expected)

    def test_get_error_status_code_on_valid_error_code(self) -> None:
        "get_error_status_code() returns the same error code on valid error code."
        error_404_code = 404
        self.assertEqual(
            self.mixin.get_error_status_code(error_404_code), error_404_code
        )

    def test_get_error_status_code_on_already_valid_self_status_error_code(
        self,
    ) -> None:
        "get_error_status_code() returns self status code if it's a valid error code."
        error_403_code = 403
        self.mixin.status = error_403_code
        self.assertEqual(
            self.mixin.get_error_status_code(self.client_error_status_400),
            error_403_code,
        )

    def test_get_error_status_code_on_non_error_code(
        self,
    ) -> None:
        "get_error_status_code() returns 400 status code on invalid passed error code."

        self.assertEqual(
            self.mixin.get_error_status_code(self.success_status_200),
            400,
        )


class DjangoViewAPIMixinSetterMethodsTest(DjangoViewAPIMixinTest):
    """DjangoViewAPIMixinTest setter methods test."""

    def setUp(self) -> None:
        """Run this setUp before each test."""
        super().setUp()
