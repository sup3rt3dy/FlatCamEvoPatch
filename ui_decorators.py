"""
Defensive UI access decorators - Prevent crashes from deleted widgets
"""
import functools
import logging

logger = logging.getLogger('base')

def safe_ui_access(func):
    """
    Decorator to safely handle UI access that may fail if widgets are deleted.
    Returns None or a sensible default if RuntimeError occurs.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                logger.debug(f"UI widget deleted in {func.__name__}: {str(e)}")
                return None
            raise
        except Exception as e:
            logger.warning(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

def safe_plot(func):
    """
    Decorator specifically for plot() methods to handle widget deletion.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            # Check if UI still exists
            if not hasattr(self, 'ui') or self.ui is None:
                logger.debug(f"UI not available for plot() in {self.__class__.__name__}")
                return
            
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                logger.debug(f"UI widget deleted during plot: {str(e)}")
                return
            raise
        except Exception as e:
            logger.warning(f"Error during plot() in {self.__class__.__name__}: {str(e)}")
            return
    return wrapper

def safe_callback(func):
    """
    Decorator for callbacks that may access deleted widgets.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                logger.debug(f"Widget deleted in callback {func.__name__}")
                return
            raise
        except Exception as e:
            logger.warning(f"Callback error in {func.__name__}: {str(e)}")
            return
    return wrapper
