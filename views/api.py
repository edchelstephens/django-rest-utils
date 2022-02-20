"""Module for our apis built using Django Rest Framework."""

from django.conf import settings
from django.views.generic.base import View
from django.http.response import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    is_success,
    is_client_error,
    is_server_error,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_403_FORBIDDEN,
)

from utils.mixins.request import DjangoRequestMixin, RestRequestMixin
from utils.exceptions import HumanReadableError
from utils.debug import (
    pprint_data,
    debug_exception,
    debugger as _debugger
)

class DjangoAPIMixin:
    """Django API base class mixin.* 
    
    Created to standardize handling request and response.

    This class has a RESPONSE class attribute, that will serve as the
    response object to be returned by child instances of this base class.

    RESPONSE class attribute must be set on child classes as class attributes as well.
    The values of which is either one of the valid RESPONSE_CLASSES listed:

    - rest_framework's Response 
               or
    - django's JsonResponse
    
    Author: 
        Edchel Stephen Nini(ESN)
        edchelstephens@gmail.com
    """

    status = 200

    RESPONSE = JsonResponse 

    CONTENT_TYPE = None

    RESPONSE_CLASSES = ( JsonResponse, Response )


    error_dict = {
        "success": False,
        "title": "Something went wrong.",
        "message": "Please contact system administrator.",
        "errors": None 
    }

    default_error_dict = {
        "success": False,
        "title": "Something went wrong.",
        "message": "Please contact system administrator.",
        "errors": None 
    }


    
    def __init__(self, *args, **kwargs):
        """Initialize base class and check validity of RESPONSE class attribute of child classes."""
        try:
            super().__init__()
            if self.RESPONSE is None:
                raise ValueError("RESPONSE object must be set")
            elif self.RESPONSE not in DjangoAPIMixin.RESPONSE_CLASSES:
                raise TypeError("Invalid RESPONSE object, must be one of {}".format(DjangoAPIMixin.RESPONSE_CLASSES))
        except Exception as exc:
            debug_exception(exc)
            raise exc

    def get_content_type(self, content_type):
        """Get view response content_type*.
        
        content_type possible values:
            None
            'text/html' 
            'text/plain'
            'application/json'
            # and others

        Defaults to class attribute CONTENT_TYPE, which can be set by children classes.

        https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpRequest.content_type
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type
        https://www.iana.org/assignments/media-types/media-types.xhtml
        """
        return content_type if content_type is not None else self.CONTENT_TYPE


    def get_response(self, data, status, content_type):
        """Get the returned response."""
        return self.RESPONSE(data=data, status=status, content_type=content_type)

    def success_response(self, data, status=200, content_type=None):
        """Method for returning success response from api."""
        if not is_success(status):
            status=200
            
        content_type = self.get_content_type(content_type)

        response = self.get_response(data, status, content_type)
        return response

    def error_response(self, exception, error_data, status=400, content_type=None):
        """Method for returning error response from api.
        
        NOTE: This should be called in the context of an except block.

        Arguments:
            exception
                - The exception instance on the Except block
            error_data
                - this is a mapping object with the same format as error_dict above.
        """

        if settings.DEBUG:
            debug_exception(exception)

        self.set_error_data(exception, error_data)
        self.set_error_status_code(status)

        content_type = self.get_content_type(content_type)
        response = self.get_response(error_data, status, content_type)
        
        return response

    def error_access_response(self, title="Unauthorized Access", message="You are not authorized to perform this operation"):
        """Return error access response data.
        
        Temporary helper method for checking revoked single employee timekeeper access
        on legacy save applications endpoints(e.g. sync logs, overtime save, etc).
        """
        try:
            error_dict = {
                "title": title,
                "message": message
            }
            
            if settings.DEBUG:
                pprint_data(error_dict, "Error Data", bg="red")
                
            return self.RESPONSE(data=error_dict, status=HTTP_403_FORBIDDEN)
        except Exception as exc:
            debug_exception(exc)
            raise exc

    def server_error_response(self, exception, message="Please contact system administrator.", title="Something went wrong.", status=500, errors=None):
        """Return default server error response with debugging."""
        self.status = status
        self.error_dict["title"] = title
        self.error_dict["message"] = message
        self.error_dict["description"] = "Something went wrong. Please contact system administrator."
        self.error_dict["errors"] = errors if errors else str(exception)
        
        return self.error_response(exception, error_data=self.error_dict, status=self.status)

    def raise_error(self, message="An error occurred", title="Something went wrong", status=400, errors=None):
        """Set status error status code and raise the human readable error."""
        self.status = status
        self.error_dict["title"] = title
        self.error_dict["message"] = message
        self.error_dict["description"] = message
        self.error_dict["errors"] = errors if errors else []
        raise HumanReadableError(message)

    def stopper(self):
        """For testing human readable exception clauses.
        
        Raises HumanReadableError.
        """
        self.raise_error(message="Stopper", title="Testing")

    def debugger(self):
        """Call utils.debug.debugger which raises RuntimeError to stop execution.
        
        Mimiced from javascript `debugger` statement.
        """
        _debugger()

    def is_error_human_readable(self, exception):
        """Check if error exception is human readable."""
        return isinstance(exception, HumanReadableError)

    def set_error_data(self, exception, error_data):
        """Ensure correct error response data - a maping object serializable to JSON.*
        
        * On this format: { 
            "title":<title>, 
            "message": <message> 
        }
        """
        try:
            if self.is_valid_error_dict(error_data):
                self.error_dict = error_data
            else:
                self.error_dict = self.default_error_dict

            if self.is_error_human_readable(exception):
                exception_message = str(exception)
                self.error_dict["message"] = exception_message
                self.error_dict["description"] = exception_message
            
        except Exception:
            self.error_dict = self.default_error_dict

    def is_valid_error_dict(self, error_data):
        """Check if error_data is in valid mapping format same as default_error_dict."""
        try:
            valid = all((
                isinstance(error_data, dict),
                "title" in error_data,
                "message" in error_data
            ))
            return valid
        except Exception:
            return False

    def set_error_status_code(self, code):
        """Verify is code is correct error status code else default to 400."""
        try:
            if self.is_valid_error_code(self.status):
                pass # self.status is already valid error code
            elif self.is_valid_error_code(code):
                self.status = code
            else:
                self.status = 400
        except Exception:
            self.status = 400

    def is_valid_error_code(self, code):
        """Check if code is valid error status code."""
        return is_client_error(code) or is_server_error(code)


class API(DjangoAPIMixin, RestRequestMixin, APIView):
    """Our class based view for rest_framework api views.
    
    https://www.django-rest-framework.org/api-guide/views/#class-based-views
    """

    RESPONSE = Response

class DjangoView(DjangoAPIMixin, DjangoRequestMixin, View):
    """Our class based view for django views.
    
    https://docs.djangoproject.com/en/3.2/topics/class-based-views/#class-based-views
    https://docs.djangoproject.com/en/3.2/ref/class-based-views/base/#view
    """

    RESPONSE = JsonResponse
