import warnings
import sys


MODES = {"WARNING", "ERROR"}


class FileTypeError(Exception): pass
class FileTypeWarning(Warning): pass

#class SyntaxError(Exception): pass
#class SyntaxWarning(Warning): pass

class UnboundParameterError(Exception): pass
class UnboundParameterWarning(Warning): pass

class UnrecognizedCommandError(Exception): pass
class UnrecognizedCommandWarning(Warning): pass

class UsageError(Exception): pass
class UsageWarning(Warning): pass


def file_type_error(message=None, mode="ERROR"):
    if mode not in MODES:
        raise ValueError("mode must be \"WARNING\" or \"ERROR\".")
    
    if message is None:
        message = f"File type {mode.lower()}."
    
    if mode == "WARNING":
        warnings.warn(message, FileTypeWarning, 3)
    else:
        raise FileTypeError(message)

def syntax_error(message=None, mode="ERROR"):
    if mode not in MODES:
        raise ValueError("mode must be \"WARNING\" or \"ERROR\".")
    
    if message is None:
        message = f"Syntax {mode.lower()}."
    
    if mode == "WARNING":
        warnings.warn(message, SyntaxWarning, 3)
    else:
        raise SyntaxError(message)

def unbound_parameter_error(message=None, mode="ERROR"):
    if mode not in MODES:
        raise ValueError("mode must be \"WARNING\" or \"ERROR\".")
    
    if message is None:
        message = f"Unbound parameter {mode.lower()}."
    
    if mode == "WARNING":
        warnings.warn(message, UnboundParameterWarning, 3)
    else:
        raise UnboundParameterError(message)

def unrecognized_command_error(message=None, mode="ERROR"):
    if mode not in MODES:
        raise ValueError("mode must be \"WARNING\" or \"ERROR\".")
    
    if message is None:
        message = f"Unrecognized command {mode.lower()}."
    
    if mode == "WARNING":
        warnings.warn(message, FileTypeWarning, 3)
    else:
        raise FileTypeError(message)

def usage_error(message=None, mode="ERROR"):
    if mode not in MODES:
        raise ValueError("mode must be \"WARNING\" or \"ERROR\".")
    
    if message is None:
        message = f"Usage {mode.lower()}."
    
    if mode == "WARNING":
        warnings.warn(message, UsageWarning, 3)
    else:
        raise UsageError(message)
