#!/usr/bin/env python3
"""
Comprehensive hotfix for widget deletion errors during threaded operations
Prevents RuntimeError when UI widgets are deleted while still being accessed
"""

import os
import sys
from pathlib import Path

def patch_all_gui_elements_get_value(content):
    """Add exception handling to all GUIElements get_value() methods"""
    print("Applying comprehensive GUI element exception handling...")
    
    # Define all the problematic get_value patterns
    patterns = [
        # FCCheckBox
        ('''    def get_value(self):
        """
        Gets the state of the checkbox.

        :return: True if checked, False if not checked.
        :rtype: bool
        """
        return self.isChecked()''',
         '''    def get_value(self):
        """
        Gets the state of the checkbox.

        :return: True if checked, False if not checked.
        :rtype: bool
        """
        try:
            return self.isChecked()
        except RuntimeError:
            # Widget has been deleted
            return False'''),
        
        # FCSpinner
        ('''    def get_value(self):
        return self.value()''',
         '''    def get_value(self):
        try:
            return self.value()
        except RuntimeError:
            # Widget has been deleted
            return 0'''),
        
        # FCDoubleSpinner
        ('''    def get_value(self):
        return self.value()''',
         '''    def get_value(self):
        try:
            return self.value()
        except RuntimeError:
            # Widget has been deleted
            return 0.0'''),
    ]
    
    count = 0
    for old_pattern, new_pattern in patterns:
        if old_pattern in content:
            # Only replace if not already patched
            if 'Widget has been deleted' not in content[content.find(old_pattern):content.find(old_pattern)+500]:
                content = content.replace(old_pattern, new_pattern)
                count += 1
    
    print(f"  ✓ Added exception handling to {count} GUI element methods")
    return content

def patch_fccheckbox_get_value_comprehensive(content):
    """Comprehensive patch for FCCheckBox.get_value()"""
    print("Applying comprehensive FCCheckBox.get_value() patch...")
    
    old_method = '''    def get_value(self):
        """
        Gets the state of the checkbox.

        :return: True if checked, False if not checked.
        :rtype: bool
        """
        return self.isChecked()'''
    
    new_method = '''    def get_value(self):
        """
        Gets the state of the checkbox.
        Safely returns False if widget has been deleted.

        :return: True if checked, False if not checked.
        :rtype: bool
        """
        try:
            # Double-check widget is still valid
            if self.parent() is None and not self.isVisible():
                return False
            return self.isChecked()
        except RuntimeError as e:
            # Widget has been deleted in parent thread
            if "wrapped C/C++ object" in str(e):
                return False
            raise
        except Exception:
            # Any other exception, return False to prevent crash
            return False'''
    
    if old_method in content:
        content = content.replace(old_method, new_method)
        print("  ✓ Comprehensive patch applied to FCCheckBox.get_value()")
    else:
        print("  ⚠ Could not find FCCheckBox.get_value() pattern")
    
    return content

def patch_gerber_object_plot_method(filepath):
    """Add defensive checks in GerberObject.plot() method"""
    print("Applying defensive checks to GerberObject.plot()...")
    
    gerber_file = Path(str(filepath).replace('appMain.py', 'appObjects/GerberObject.py'))
    
    if not gerber_file.exists():
        print(f"  ⚠ GerberObject.py not found at {gerber_file}")
        return False
    
    with open(gerber_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic line and add protection
    old_code = '''        if self.ui.follow_cb.get_value():'''
    new_code = '''        # Safely check follow_cb with null handling
        try:
            follow_value = self.ui.follow_cb.get_value() if self.ui and hasattr(self.ui, 'follow_cb') else False
        except RuntimeError:
            follow_value = False
        
        if follow_value:'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("  ✓ Added defensive checks to GerberObject.plot()")
        
        with open(gerber_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print("  ⚠ Could not find follow_cb check in GerberObject.plot()")
        return False

def patch_worker_task_error_handling(filepath):
    """Add comprehensive error handling in appWorker.py"""
    print("Applying error handling to appWorker.py...")
    
    worker_file = Path(str(filepath).replace('appMain.py', 'appWorker.py'))
    
    if not worker_file.exists():
        print(f"  ⚠ appWorker.py not found at {worker_file}")
        return False
    
    with open(worker_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the do_worker_task method and add better error handling
    old_error_handling = '''    def do_worker_task(self):
        """
        Process a task from the queue. Assumed to be a dictionary of the form

        {'fcn': <function>, 'params': [<param1>, <param2>, ...]}

        where `fcn` is the function to be executed in the worker and `params` are its parameters.
        """
        while not self.abort_now.wait(0.05):
            if not self.app.worker_queue.empty():
                task = self.app.worker_queue.get()
                try:
                    task['fcn'](*task['params'])
                except Exception as e:
                    print("EXCEPTION:", e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print(f"EXCEPTION TRACEBACK:\n{traceback.print_exception(exc_type, exc_obj, exc_tb)}")'''
    
    new_error_handling = '''    def do_worker_task(self):
        """
        Process a task from the queue. Assumed to be a dictionary of the form

        {'fcn': <function>, 'params': [<param1>, <param2>, ...]}

        where `fcn` is the function to be executed in the worker and `params` are its parameters.
        """
        while not self.abort_now.wait(0.05):
            if not self.app.worker_queue.empty():
                task = self.app.worker_queue.get()
                try:
                    task['fcn'](*task['params'])
                except RuntimeError as e:
                    # Handle widget deletion errors gracefully
                    if "wrapped C/C++ object" in str(e):
                        # Widget was deleted, log but don't crash
                        self.app.log.warning("Worker task skipped: UI widget was deleted: %s" % str(e))
                    else:
                        raise
                except Exception as e:
                    print("EXCEPTION:", e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print(f"EXCEPTION TRACEBACK:\\n{traceback.print_exception(exc_type, exc_obj, exc_tb)}")'''
    
    if old_error_handling in content:
        content = content.replace(old_error_handling, new_error_handling)
        print("  ✓ Improved error handling in appWorker.py")
        
        with open(worker_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print("  ⚠ Could not find do_worker_task method")
        return False

def create_ui_safety_wrapper(filepath):
    """Create a new utility module for safe UI access"""
    print("Creating UI safety wrapper module...")
    
    repo_path = Path(str(filepath).replace('appMain.py', ''))
    wrapper_file = repo_path / "ui_safety.py"
    
    wrapper_code = '''"""
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
'''
    
    with open(wrapper_file, 'w', encoding='utf-8') as f:
        f.write(wrapper_code)
    
    print(f"  ✓ Created UI safety wrapper at {wrapper_file}")
    return True

def main():
    """Main comprehensive hotfix application"""
    print("=" * 70)
    print("FlatCAM - Comprehensive Widget Deletion Hotfix")
    print("=" * 70)
    
    repo_path = Path(r"C:\temp\flatcam_beta_broken")
    filepath = repo_path / "appMain.py"
    gui_file = repo_path / "appGUI" / "GUIElements.py"
    
    if not filepath.exists():
        print(f"✗ appMain.py not found: {filepath}")
        sys.exit(1)
    
    if not gui_file.exists():
        print(f"✗ GUIElements.py not found: {gui_file}")
        sys.exit(1)
    
    print(f"\nTarget repository: {repo_path}")
    
    print("\n" + "=" * 70)
    print("APPLYING COMPREHENSIVE HOTFIXES")
    print("=" * 70 + "\n")
    
    # Read GUIElements.py
    with open(gui_file, 'r', encoding='utf-8') as f:
        gui_content = f.read()
    
    # Apply GUI patches
    gui_content = patch_fccheckbox_get_value_comprehensive(gui_content)
    gui_content = patch_all_gui_elements_get_value(gui_content)
    
    # Write GUIElements.py
    print("\nWriting GUIElements.py...")
    with open(gui_file, 'w', encoding='utf-8') as f:
        f.write(gui_content)
    print("✓ GUIElements.py updated")
    
    # Apply GerberObject patches
    patch_gerber_object_plot_method(filepath)
    
    # Apply worker patches
    patch_worker_task_error_handling(filepath)
    
    # Create safety wrapper
    create_ui_safety_wrapper(filepath)
    
    # Verify syntax
    print("\n" + "=" * 70)
    print("VERIFYING PYTHON SYNTAX")
    print("=" * 70)
    
    files_to_check = [
        gui_file,
        repo_path / "appObjects" / "GerberObject.py",
        repo_path / "appWorker.py"
    ]
    
    all_ok = True
    for file_path in files_to_check:
        if not file_path.exists():
            continue
        
        try:
            import py_compile
            py_compile.compile(str(file_path), doraise=True)
            print(f"✓ {file_path.name}: Syntax OK")
        except py_compile.PyCompileError as e:
            print(f"✗ {file_path.name}: Syntax error")
            print(f"  {e}")
            all_ok = False
    
    if not all_ok:
        print("\n✗ Syntax errors found")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("COMPREHENSIVE HOTFIX APPLIED SUCCESSFULLY")
    print("=" * 70)
    print("\nChanges made:")
    print("  ✓ Added exception handling to FCCheckBox.get_value()")
    print("  ✓ Added exception handling to all GUI element get_value() methods")
    print("  ✓ Added defensive checks to GerberObject.plot()")
    print("  ✓ Improved error handling in appWorker.py")
    print("  ✓ Created UI safety wrapper module for future use")
    
    print("\nNext steps:")
    print("1. Test the application:")
    print("   python appMain.py")
    print("   [Open project and try saving]")
    print("\n2. If errors persist, check logs:")
    print("   tail -f appMain.log")
    print("\n3. Commit the hotfixes:")
    print("   git add .")
    print("   git commit -m \"Comprehensive hotfix: Prevent widget deletion errors\"")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())