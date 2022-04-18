import sys

from django.conf import settings
from django.utils.termcolors import colorize

from logging.loggers import TerminalLoggingMixin


class DebuggerMixin(TerminalLoggingMixin):
    """Debugger mixin."""


    def print_debug_multiline(self, label:str, exception_object:Exception, exception_type:type, code:str, location:str, line_number:int, bg:str) -> None:
        """Print exception info nicely in multilines with label."""
        try:
            print()
            self.pprint_label(label, bg=bg)
            print("Exception:", self.make_bold(str(exception_object), fg=bg))
            print("Type:", self.make_bold(exception_type, fg=bg)) 
            print("Function/Method/Caller:", self.make_bold(code, fg=bg))
            print("Location:", self.make_bold(location, fg=bg))
            print("Line:", self.make_bold(line_number, fg=bg))
            self.pprint_symbols(symbol_repetition=42 + len(label), bg=bg)
        except Exception as exc:
            pass

    def print_debug_single_line(self, exception_object:Exception, exception_type:type, location:str, code:str, line_number:int, bg:str) -> None:
        """Print exception info in single line with bg background."""
        try:
            one_line_error = "{} {} {} Caller: {}() Line: {}".format(
                exception_object, 
                exception_type,
                location,  
                code, 
                line_number
            )
            print(colorize(one_line_error, opts=("bold", "underscore"), fg=bg))
        except Exception as exc:
            pass


    def debug_exception(self, exception:Exception, label="Exception Occurred", bg="red"):
        """Print exception and traceback info for developers to debug.
        
        NOTE: This should be called on the context of an except clause:
        ..
        except Exception as exc:
            debug_exception(exc)
        ..

        https://docs.python.org/3/library/sys.html#sys.exc_info
        """
        try:
            exception_type, exception_object, exc_traceback = sys.exc_info()
            exc_frame = exc_traceback.tb_frame
            f_code = exc_frame.f_code
            
            code = f_code.co_name
            location = f_code.co_filename.split(settings.BASE_DIR)[1]
            line_number = exc_traceback.tb_lineno

            if settings.DEBUG_MULTILINE:
                self.print_debug_multiline(label, exception_object, exception_type, code, location, line_number, bg)
            else:
                self.print_debug_single_line(exception_object, exception_type, location, code, line_number, bg)
        
        except Exception as e:
            self.pprint_data(exception, "An exception occurred", bg="red")

    def debugger(self, message:str) -> None:
        """Call utils.debug.debugger which raises RuntimeError to stop execution.
        
        Mimiced from javascript `debugger` statement.
        """
        raise RuntimeError(message)

