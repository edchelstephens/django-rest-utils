"""Utils for logging.."""

from pprint import pprint
from typing import Any

from django.utils.termcolors import colorize


class TerminalLoggingMixin:
    """Mixin for terminal logging."""

    def make_bold(self, text:str, fg="red") -> str:
        """Return text as bolded"""
        return colorize(text, opts=("bold",), fg=fg)

    def pprint_symbols(self, symbol="=", symbol_repetition=42, bg="green") -> str:
        """Print colorized symbol repeated."""
        print(colorize(symbol*symbol_repetition, opts=("bold",), fg="white", bg=bg))

    def pprint_label(
        self, label="DATA", symbol="=", symbol_repetition=20, fg="white", bg="green"
    ) -> None:
        """Prints label string, surrounded by repeated symbols."""
        symboled_label = "{} {} {}".format(
            symbol * symbol_repetition, label, symbol * symbol_repetition
        )
        colorized_label = colorize(symboled_label, opts=("bold",), fg=fg, bg=bg)
        print(colorized_label)

    def pprint_data(self, data: Any, label="DATA") -> None:
        """Pretty print data with label."""
        print()
        self.pprint_label(label=label)
        pprint(data)
        print()

    def pprint_response(self, response: Any, label="RESPONSE") -> None:
        """Pretty print response, a shorthand for pprint_data(data=response, label='Response')"""
        self.pprint_data(data=response, label=label)

    def pprint_type(self, data: Any, label="Type") -> None:
        """Pretty print type of object data."""
        self.pprint_data(type(data), label=label)

    def pprint_dir(self, data: Any, label="dir(data)") -> None:
        """Pretty print dir(data)."""
        self.pprint_data(data=dir(data), label=label)

    def pprint_dict(self, data: Any, label="data.__dict__") -> None:
        """Pretty print data.__dict__."""
        try:
            self.pprint_data(data=data.__dict__, label=label)
        except AttributeError:
            self.pprint_label(label="Unable to print .__dict__")
            print(
                "Object: {}  of type: {} has no attribute .__dict__".format(
                    data, type(data)
                )
            )

    def pprint_breakpoint(self, label="BREAK POINT", symbol="*") -> None:
        """Print a break point line."""
        print()
        self.pprint_label(label=label, symbol=symbol, symbol_repetition=30, bg="red")
        print()

    def pprint_locals(self, local_vars: dict) -> None:
        """Pretty print local variables `local_vars` from locals() returned dictionary.
        Sample invocation:
            self.pprint_locals(locals())
        """
        self.pprint_data(local_vars, label="Local Variables")