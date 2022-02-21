from .exceptions import HumanReadableError

class DebuggerMixin:

    def debugger(self, message:str) -> None:
        """Call utils.debug.debugger which raises RuntimeError to stop execution.
        
        Mimiced from javascript `debugger` statement.
        """
        raise RuntimeError(message)