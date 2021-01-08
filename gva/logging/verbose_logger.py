import functools
import logging
from .logger import get_logger
from inspect import getframeinfo, stack
import sys
import re
import os
import time

def verbose_logger(_func=None):
    def log_decorator_info(func):
        @functools.wraps(func)
        def log_decorator_wrapper(*args, **kwargs):
            # Build logger object
            logger = get_logger()

            """ Create a list of the positional arguments passed to function.
            - Using repr() for string representation for each argument. repr() is similar to str() only difference being
             it prints with a pair of quotes and if we calculate a value we get more precise value than str(). """
            args_passed_in_function = [repr(a) for a in args]
            """ Create a list of the keyword arguments. The f-string formats each argument as key=value, where the !r 
                specifier means that repr() is used to represent the value. """
            kwargs_passed_in_function = [f"{k}={v!r}" for k, v in kwargs.items()]

            """ The lists of positional and keyword arguments is joined together to form final string """
            formatted_arguments = ", ".join(args_passed_in_function + kwargs_passed_in_function)

            """ Generate file name and function name for calling function. __func.name__ will give the name of the 
                caller function ie. wrapper_log_info and caller file name ie log-decorator.py
            - In order to get actual function and file name we will use 'extra' parameter.
            - To get the file name we are using in-built module inspect.getframeinfo which returns calling file name """
            py_file_caller = getframeinfo(stack()[1][0])

            """ Before to the function execution, log function details."""
            logger.debug(f"Call: {func.__name__}({formatted_arguments}) - {os.path.basename(py_file_caller.filename)}")
            try:
                start = time.process_time_ns()
                """ log return value from the function """
                value = func(*args, **kwargs)
                execution_time = (time.process_time_ns() - start) / 1e9
                try:
                    display = str(repr(value))
                    display = display.replace('\n', '')
                    display = display.replace('\r', '')
                    display = re.sub(r"[^0-9a-zA-Z\{\}\-\+\=\<\>\:\'\.\[\]\_\-]+", "", display)
                    display = display[0:100]
                except:
                    display = "[NON-PRINTABLE]"
                logger.debug(f"Return after {execution_time}s: {func.__name__}() - {display}")
            except Exception as e:
                """log exception if occurs in function"""
                logger.error(f"Exception: {func.__name__}() - {str(sys.exc_info()[1])} {e.__class__.__name__} - {e.args[0]}")
                raise
            # Return function value
            return value
        # Return the pointer to the function
        return log_decorator_wrapper
    # Decorator was called with arguments, so return a decorator function that can read and return a function
    if _func is None:
        return log_decorator_info
    # Decorator was called without arguments, so apply the decorator to the function immediately
    else:
        return log_decorator_info(_func)