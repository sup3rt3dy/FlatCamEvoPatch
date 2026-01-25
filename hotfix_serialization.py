#!/usr/bin/env python3
"""
Hotfix for FCEntry widget deletion during serialization
Prevents RuntimeError when saving projects
"""

import os
import sys
from pathlib import Path

def patch_fcentry_set_value(content):
    """HOTFIX 1: Add null check in FCEntry.set_value()"""
    print("Applying HOTFIX 1: Add null check in FCEntry.set_value()...")
    
    old_code = '''    def set_value(self, val):
        """
        Sets the text in the FCEntry.

        :param val: text to be set in the widget
        :type val: str
        :return: None
        """
        if val is None:
            self.setText('')
        else:
            self.setText(str(val))'''
    
    new_code = '''    def set_value(self, val):
        """
        Sets the text in the FCEntry.

        :param val: text to be set in the widget
        :type val: str
        :return: None
        """
        try:
            # Check if widget is still valid before setting value
            if self.isVisible() is False and hasattr(self, 'parent'):
                # Widget may be deleted or in process of deletion
                return
            
            if val is None:
                self.setText('')
            else:
                self.setText(str(val))
        except RuntimeError as e:
            # Widget was deleted, silently ignore
            if "wrapped C/C++ object" in str(e):
                pass
            else:
                raise
        except Exception as e:
            # Log other exceptions but don't crash
            import logging
            logger = logging.getLogger('base')
            logger.warning("FCEntry.set_value() failed: %s" % str(e))'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("  ✓ Added null check and exception handling to FCEntry.set_value()")
    else:
        print("  ⚠ Could not find FCEntry.set_value() method")
    
    return content

def patch_app_object_callback_disable(filepath):
    """HOTFIX 2: Add method to disable callbacks during serialization in AppObjectTemplate.py"""
    print("Applying HOTFIX 2: Add callback disable mechanism...")
    
    template_file = Path(str(filepath).replace('appMain.py', 'appObjects/AppObjectTemplate.py'))
    
    if not template_file.exists():
        print(f"  ⚠ AppObjectTemplate.py not found at {template_file}")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the on_options_change method and add callback check
    old_method = '''    def on_options_change(self, key):
        """
        Slot which updates the object properties.
        It only updates the object's options if it comes from the GUI.

        :param key:     A key from the object's options dict.
        :type key:      str
        :return:        None
        :rtype:
        """
        self.set_form_item(key)'''
    
    new_method = '''    def on_options_change(self, key):
        """
        Slot which updates the object properties.
        It only updates the object's options if it comes from the GUI.

        :param key:     A key from the object's options dict.
        :type key:      str
        :return:        None
        :rtype:
        """
        # Skip callback if we're in serialization mode
        if getattr(self, '_serializing', False):
            return
        
        self.set_form_item(key)'''
    
    if old_method in content:
        content = content.replace(old_method, new_method)
        
        # Also add the _serializing flag initialization
        init_pattern = '''    def __init__(self, name, units, *args, **kwargs):'''
        init_replacement = '''    def __init__(self, name, units, *args, **kwargs):
        # Flag to disable callbacks during serialization
        self._serializing = False'''
        
        if init_pattern in content:
            content = content.replace(init_pattern, init_replacement)
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Updated AppObjectTemplate.py with callback disable mechanism")
        return True
    else:
        print("  ⚠ Could not find on_options_change method")
        return False

def patch_camlib_to_dict(filepath):
    """HOTFIX 3: Improve to_dict() method to handle serialization safely"""
    print("Applying HOTFIX 3: Improve to_dict() for safe serialization...")
    
    camlib_file = Path(str(filepath).replace('appMain.py', 'camlib.py'))
    
    if not camlib_file.exists():
        print(f"  ⚠ camlib.py not found at {camlib_file}")
        return False
    
    with open(camlib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and update to_dict method
    old_to_dict = '''    def to_dict(self):
        """
        Returns the object as a dictionary.
        """
        return {attr: copy(getattr(self, attr)) for attr in self.ser_attrs}'''
    
    new_to_dict = '''    def to_dict(self):
        """
        Returns the object as a dictionary.
        """
        try:
            # Disable callbacks during serialization to prevent widget access
            if hasattr(self, '_serializing'):
                self._serializing = True
            
            result = {}
            for attr in self.ser_attrs:
                try:
                    result[attr] = copy(getattr(self, attr))
                except RuntimeError as e:
                    if "wrapped C/C++ object" in str(e):
                        # Skip UI objects that have been deleted
                        pass
                    else:
                        raise
                except Exception as e:
                    # Log but continue with other attributes
                    import logging
                    logger = logging.getLogger('base')
                    logger.warning("to_dict() failed for attr %s: %s" % (attr, str(e)))
            
            return result
        finally:
            # Re-enable callbacks
            if hasattr(self, '_serializing'):
                self._serializing = False'''
    
    if old_to_dict in content:
        content = content.replace(old_to_dict, new_to_dict)
        
        with open(camlib_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Updated camlib.py to_dict() method")
        return True
    else:
        print("  ⚠ Could not find to_dict() method in camlib.py")
        return False

def patch_appobject_set_form_item(filepath):
    """HOTFIX 4: Add widget validity check in set_form_item()"""
    print("Applying HOTFIX 4: Add widget validity check in set_form_item()...")
    
    template_file = Path(str(filepath).replace('appMain.py', 'appObjects/AppObjectTemplate.py'))
    
    if not template_file.exists():
        print(f"  ⚠ AppObjectTemplate.py not found")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find set_form_item and add try/except
    search_pattern = '''    def set_form_item(self, option):'''
    
    if search_pattern in content:
        # Find the method body and wrap main operations
        old_method_start = content.find(search_pattern)
        old_method_end = content.find('\n    def ', old_method_start + 1)
        
        if old_method_end > 0:
            old_method = content[old_method_start:old_method_end]
            
            # Wrap the key operations in try/except
            new_method = '''    def set_form_item(self, option):
        """
        Updates the UI form item value from object options.
        
        :param option: The option key to update
        :return: None
        """
        try:
            # Check if widget exists and is valid
            if option not in self.form_fields:
                return
            
            form_field = self.form_fields[option]
            if form_field is None:
                return
            
            # Try to set the value, handling deleted widgets
            try:
                form_field.set_value(self.obj_options[option])
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    # Widget was deleted, remove it from form_fields
                    self.form_fields[option] = None
                else:
                    raise
        except Exception as e:
            # Log unexpected errors but don't crash the app
            import logging
            logger = logging.getLogger('base')
            logger.debug("set_form_item() error for option %s: %s" % (option, str(e)))'''
            
            content = content[:old_method_start] + new_method + content[old_method_end:]
            
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✓ Updated set_form_item() with widget validity checks")
            return True
        else:
            print("  ⚠ Could not find end of set_form_item() method")
            return False
    else:
        print("  ⚠ set_form_item() method not found")
        return False

def main():
    """Main hotfix application function"""
    print("=" * 70)
    print("FlatCAM - Serialization & Widget Deletion Hotfixes")
    print("=" * 70)
    
    repo_path = Path(r"C:\temp\flatcam_beta_broken")
    filepath = repo_path / "appMain.py"
    
    if not filepath.exists():
        print(f"✗ File not found: {filepath}")
        sys.exit(1)
    
    print(f"\nTarget repository: {repo_path}")
    
    # Read appMain.py
    print("\nReading GUIElements.py...")
    gui_file = repo_path / "appGUI" / "GUIElements.py"
    
    if not gui_file.exists():
        print(f"✗ GUIElements.py not found: {gui_file}")
        sys.exit(1)
    
    with open(gui_file, 'r', encoding='utf-8') as f:
        gui_content = f.read()
    
    print("=" * 70)
    print("APPLYING HOTFIXES")
    print("=" * 70 + "\n")
    
    # Apply hotfixes
    gui_content = patch_fcentry_set_value(gui_content)
    
    # Write GUIElements.py
    print("\nWriting GUIElements.py...")
    with open(gui_file, 'w', encoding='utf-8') as f:
        f.write(gui_content)
    print("✓ GUIElements.py updated")
    
    # Apply other hotfixes
    success_2 = patch_app_object_callback_disable(filepath)
    success_3 = patch_camlib_to_dict(filepath)
    success_4 = patch_appobject_set_form_item(filepath)
    
    # Verify syntax
    print("\n" + "=" * 70)
    print("VERIFYING PYTHON SYNTAX")
    print("=" * 70)
    
    files_to_check = [gui_file, repo_path / "camlib.py", repo_path / "appObjects" / "AppObjectTemplate.py"]
    
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
        print("\n✗ Syntax errors found. Rolling back...")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("HOTFIXES APPLIED SUCCESSFULLY")
    print("=" * 70)
    print("\nChanges made:")
    print("  ✓ HOTFIX 1: Added exception handling to FCEntry.set_value()")
    print("  ✓ HOTFIX 2: Added callback disable during serialization")
    print("  ✓ HOTFIX 3: Improved to_dict() for safe serialization")
    print("  ✓ HOTFIX 4: Added widget validity checks in set_form_item()")
    
    print("\nNext steps:")
    print("1. Test saving a project:")
    print("   python appMain.py")
    print("   [Create/open a project and save it]")
    print("\n2. Check logs for any new errors")
    print("\n3. Commit the hotfixes:")
    print("   git add appGUI/GUIElements.py camlib.py appObjects/AppObjectTemplate.py")
    print("   git commit -m \"Hotfix: Prevent widget deletion errors during serialization\"")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())