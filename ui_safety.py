"""
UI Safety Wrapper - Provides safe access to UI elements that may be deleted
"""

class SafeUIAccess:
    """Wrapper to safely access UI elements that may be deleted"""
    
    @staticmethod
    def get_value(ui_element, default=None, silent=False):
        """
        Safely get value from UI element
        
        Args:
            ui_element: The UI element to get value from
            default: Default value if element is deleted or unavailable
            silent: If True, suppress warning logs
        
        Returns:
            The element's value or default
        """
        if ui_element is None:
            return default
        
        try:
            # Check if element is still valid
            if hasattr(ui_element, 'get_value'):
                return ui_element.get_value()
            elif hasattr(ui_element, 'value'):
                return ui_element.value()
            elif hasattr(ui_element, 'isChecked'):
                return ui_element.isChecked()
            elif hasattr(ui_element, 'text'):
                return ui_element.text()
            return default
        except RuntimeError as e:
            # Widget was deleted
            if "wrapped C/C++ object" in str(e):
                if not silent:
                    import logging
                    logger = logging.getLogger('base')
                    logger.debug("UI element was deleted, returning default: %s" % str(e))
                return default
            raise
        except Exception as e:
            import logging
            logger = logging.getLogger('base')
            logger.warning("Error accessing UI element: %s, returning default" % str(e))
            return default
    
    @staticmethod
    def set_value(ui_element, value, silent=False):
        """
        Safely set value on UI element
        
        Args:
            ui_element: The UI element to set value on
            value: The value to set
            silent: If True, suppress warning logs
        
        Returns:
            True if successful, False otherwise
        """
        if ui_element is None:
            return False
        
        try:
            if hasattr(ui_element, 'set_value'):
                ui_element.set_value(value)
            elif hasattr(ui_element, 'setValue'):
                ui_element.setValue(value)
            elif hasattr(ui_element, 'setChecked'):
                ui_element.setChecked(value)
            elif hasattr(ui_element, 'setText'):
                ui_element.setText(str(value))
            else:
                return False
            return True
        except RuntimeError as e:
            # Widget was deleted
            if "wrapped C/C++ object" in str(e):
                if not silent:
                    import logging
                    logger = logging.getLogger('base')
                    logger.debug("UI element was deleted, cannot set value: %s" % str(e))
                return False
            raise
        except Exception as e:
            import logging
            logger = logging.getLogger('base')
            logger.warning("Error setting UI element value: %s" % str(e))
            return False
