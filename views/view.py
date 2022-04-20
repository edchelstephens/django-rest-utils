"""Module for views wrappers."""

from typing import Optional, List


from django.conf import settings
from django.views.generic.base import View
from django.http.response import JsonResponse, HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    is_success,
    is_client_error,
    is_server_error,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from views.request import DjangoRequestMixin, RestRequestMixin
from exceptions import HumanReadableError
from debug.debug import DebuggerMixin


RequestResponseData = list | dict

class DjangoViewAPIMixin(DebuggerMixin):
    """Django View API base class mixin.* 
    
    Created to standardize handling request and response.

    This class has a RESPONSE class attribute, that will serve as the
    response object to be returned by child instances of this base class.

    RESPONSE class attribute must be set on child classes as class attributes as well.
    The values of which is either one of the valid RESPONSE_CLASSES listed:

    - rest_framework's Response 
               or
    - django's JsonResponse
    
    """

    status = 200
    RESPONSE = JsonResponse 
    CONTENT_TYPE = "application/json"

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

    def get_content_type(self, content_type:str) -> str:
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


    def get_response(self, data:RequestResponseData, status:int, content_type:str, **kwargs) -> HttpResponse:
        """Get the returned response."""
        try:
            return self.RESPONSE(data=data, status=status, content_type=content_type, **kwargs)
        except Exception:
            return self.RESPONSE(data=data, status=status, content_type=content_type)

    def success_response(self, data:RequestResponseData, status=200, content_type:Optional["str"]=None) -> HttpResponse:
        """Method for returning success response from api."""
        if not is_success(status):
            status=200
            
        content_type = self.get_content_type(content_type)

        response = self.get_response(data, status, content_type)
        return response

    def error_response(self, exception:Exception, error_data:dict, status=400, content_type:Optional["str"]=None) -> HttpResponse:
        """Method for returning error response from api.
        
        NOTE: This should be called in the context of an except block.

        Arguments:
            exception
                - The exception instance on the Except block
            error_data
                - this is a mapping object with the same format as error_dict above.
        """

        if settings.DEBUG:
            self.debug_exception(exception)

        self.set_error_data(exception, error_data)
        self.set_error_status_code(status)

        content_type = self.get_content_type(content_type)
        response = self.get_response(error_data, status, content_type)
        
        return response


    def server_error_response(self, 
        exception:Exception, 
        message="Please contact system administrator.", 
        title="Something went wrong.", 
        status=HTTP_500_INTERNAL_SERVER_ERROR, 
        errors:Optional[List]=None) -> HttpResponse:
        """Return default server error response with debugging."""
        self.status = status
        self.error_dict["title"] = title
        self.error_dict["message"] = message
        self.error_dict["errors"] = errors if errors else str(exception)
        
        return self.error_response(exception, error_data=self.error_dict, status=self.status)

    def raise_error(self, message="An error occurred", title="Something went wrong", status=400, errors:Optional[List]=None) -> None:
        """Set status error status code and raise the human readable error."""
        self.status = status
        self.error_dict["title"] = title
        self.error_dict["message"] = message
        self.error_dict["errors"] = errors if errors else []
        raise HumanReadableError(message)

    def stopper(self) -> None:
        """For testing human readable exception clauses.
        
        Raises HumanReadableError.
        """
        self.raise_error(message="Stopper", title="Testing")

    def is_error_human_readable(self, exception:Exception) -> bool:
        """Check if error exception is human readable."""
        return isinstance(exception, HumanReadableError)

    def set_error_data(self, exception:Exception, error_data:dict) -> None:
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
            
        except Exception:
            self.error_dict = self.default_error_dict

    def is_valid_error_dict(self, error_data:dict) -> bool:
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

    def set_error_status_code(self, code:int) -> None:
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

    def is_valid_error_code(self, code:int) -> bool:
        """Check if code is valid error status code."""
        return is_client_error(code) or is_server_error(code)


class RestAPIView(DjangoViewAPIMixin, RestRequestMixin, APIView):
    """Our class based view for rest_framework api views.
    
    https://www.django-rest-framework.org/api-guide/views/#class-based-views
    """

    RESPONSE = Response

class DjangoView(DjangoViewAPIMixin, DjangoRequestMixin, View):
    """Our class based view for django views.
    
    https://docs.djangoproject.com/en/3.2/topics/class-based-views/#class-based-views
    https://docs.djangoproject.com/en/3.2/ref/class-based-views/base/#view
    """

    RESPONSE = JsonResponse
