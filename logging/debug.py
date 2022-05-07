import sys
import os
import pytz

from datetime import tzinfo
from types import CodeType

from django.conf import settings
from django.utils.termcolors import colorize
from django.utils import timezone

from logging.logging import TerminalLoggingMixin


class DebuggerMixin(TerminalLoggingMixin):
    """Debugger mixin."""

    def print_debug_multiline(
        self,
        label: str,
        timestamp: str,
        exception_object: Exception,
        exception_type: type,
        caller: str,
        location: str,
        line_number: int,
        bg: str,
    ) -> None:
        """Print exception info nicely in multilines with label."""
        try:
            print()
            self.pprint_label(label, bg=bg)
            print("Timestamp:", self.make_bold(timestamp, fg=bg))
            print("Exception:", self.make_bold(str(exception_object), fg=bg))
            print("Type:", self.make_bold(exception_type, fg=bg))
            print("Caller:", self.make_bold(text="{}()".format(caller), fg=bg))
            print("Location:", self.make_bold(location, fg=bg))
            print("Line:", self.make_bold(line_number, fg=bg))
            self.pprint_symbols(symbol_repetition=42 + len(label), bg=bg)
        except Exception as exc:
            self.pprint_exception(exc, "Exception occured on trying to debug exception")
            self.pprint_exception(exception_object)

    def print_debug_single_line(
        self,
        timestamp: str,
        exception_object: Exception,
        exception_type: type,
        location: str,
        caller: str,
        line_number: int,
        bg: str,
    ) -> None:
        """Print exception info in single line with bg background."""
        try:
            one_line_error = "{} -> Exception:{} -> Type:{} -> Caller:{}() -> Location:{} -> Line:{}".format(
                timestamp,
                exception_object,
                exception_type.__name__,
                caller,
                location,
                line_number,
            )
            print(colorize(one_line_error, opts=("bold", "underscore"), fg=bg))
        except Exception as exc:
            self.pprint_exception(exc, "Exception occured on trying to debug exception")
            self.pprint_exception(exception_object)

    def get_caller(self, code_type: CodeType) -> str:
        """Get caller string."""
        code = code_type.co_name
        caller = code
        instance_name = self.__class__.__name__
        if instance_name != "DebuggerMixin":
            caller = "{}.{}".format(instance_name, code)

        return caller

    def get_project_root_dir(self) -> str:
        """Return project root directory string."""
        return str(settings.BASE_DIR.parent)

    def get_location(self, code_type: CodeType) -> str:
        """Return file location."""
        root = self.get_project_root_dir()
        fullpath = code_type.co_filename
        location = fullpath.split(root)[1]

        return location

    def is_debug_multiline(self) -> bool:
        """Check if to print debug line in multiline."""
        try:
            return os.environ.get("DEBUG_MULTILINE") == "True"
        except Exception:
            return False

    def is_debug_timezone_ph(self) -> bool:
        """Check if print debug in PH time."""
        try:
            return os.environ.get("DEBUG_TIMEZONE_PH") == "True"
        except Exception as exc:
            return False

    def get_debug_timezone(self) -> tzinfo:
        """Get debug timezone."""
        au_melbourne = pytz.timezone("Australia/Melbourne")
        asia_singapore = pytz.timezone("Asia/Singapore")

        debug_timezone = au_melbourne
        if self.is_debug_timezone_ph():
            debug_timezone = asia_singapore

        return debug_timezone

    def get_timestamp(self) -> str:
        """Return current timestamp on this format:

        2022-05-06 02:35 AM
        """
        date_format = "%Y-%m-%d"
        time_format = "%I:%M %p "
        datetime_format = date_format + " " + time_format

        timezone_now = timezone.now()
        debug_timezone = self.get_debug_timezone()
        timestamp = timezone_now.astimezone(debug_timezone)
        timestamp_string = timestamp.strftime(datetime_format)

        return timestamp_string

    def debug_exception(
        self, exception: Exception, label="Exception Occurred", bg="red"
    ) -> None:
        """Print exception and traceback info for developers to debug.

        NOTE: This should be called on the context of an except clause:
        ..
        except Exception as exc:
            self.debug_exception(exc)
        ..

        https://docs.python.org/3/library/sys.html#sys.exc_info
        """
        try:
            exception_type, exception_object, exception_traceback = sys.exc_info()

            exception_frame = exception_traceback.tb_frame
            code_type = exception_frame.f_code

            caller = self.get_caller(code_type)
            location = self.get_location(code_type)
            line_number = exception_traceback.tb_lineno
            timestamp = self.get_timestamp()

            if self.is_debug_multiline():
                self.print_debug_multiline(
                    label,
                    timestamp,
                    exception_object,
                    exception_type,
                    caller,
                    location,
                    line_number,
                    bg,
                )
            else:
                self.print_debug_single_line(
                    timestamp,
                    exception_object,
                    exception_type,
                    location,
                    caller,
                    line_number,
                    bg,
                )

        except Exception as e:
            self.pprint_exception(e, "Exception occured on trying to debug exception")
            self.pprint_exception(exception, "Exception")


terminal_debug_logger = DebuggerMixin()
