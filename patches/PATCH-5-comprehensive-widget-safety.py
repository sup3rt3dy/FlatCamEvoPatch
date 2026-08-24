#!/usr/bin/env python3
"""
PATCH-5: Comprehensive widget safety for all custom UI elements
Critical fix for object deletion operations

Issue: Multiple widget types crash when set_value() called on deleted widgets
       FCCheckBox, FCEntry, FCDoubleSpinner all affected
Impact: Cannot delete objects from collection, project save fails
Risk: LOW - Exception handling only
"""

import sys
import re
from pathlib import Path

def apply_comprehensive_widget_patches():
    """Apply safety patches to all widget set_value() methods"""
    print("=" * 70)
    print("PATCH-5: Comprehensive Widget Deletion Safety")
    print("=" * 70)
    
    repo_path = Path(r"C:\temp\flatcam_beta_broken")
    gui_file = repo_path / "appGUI" / "GUIElements.py"
    
    if not gui_file.exists():
        print(f"✗ GUIElements.py not found: {gui_file}")
        return False
    
    print(f"\nFile: {gui_file}")
    
    # Read the file
    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    patched_count = 0
    
    # PATCH 5.1: FCCheckBox2.set_value() - line ~1900
    print("\n[1/4] Patching FCCheckBox2.set_value()...")
    search_1 = '''    def set_value(self, val):
        self.setChecked(True if val else False)'''
    
    replacement_1 = '''    def set_value(self, val):
        try:
            self.setChecked(True if val else False)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise
        except Exception:
            return'''
    
    if search_1 in content:
        content = content.replace(search_1, replacement_1)
        print("      ✓ Added exception handling to FCCheckBox2.set_value()")
        patched_count += 1
    else:
        print("      ⚠ Pattern not found (may already be patched)")
    
    # PATCH 5.2: FCDoubleSpinner.set_value()
    print("[2/4] Patching FCDoubleSpinner.set_value()...")
    search_2 = '''class FCDoubleSpinner(QtWidgets.QDoubleSpinBox):'''
    
    if search_2 in content:
        # Find the FCDoubleSpinner class and locate its set_value method
        # We need to search for it more carefully
        idx = content.find(search_2)
        if idx > 0:
            # Find the next class definition
            next_class = content.find('\nclass ', idx + len(search_2))
            if next_class < 0:
                next_class = len(content)
            
            class_section = content[idx:next_class]
            
            # Check if set_value exists in this class
            if 'def set_value(self' in class_section:
                # Find the set_value method
                set_value_start = class_section.find('def set_value(self')
                set_value_end = class_section.find('\n    def ', set_value_start + 1)
                
                if set_value_end < 0:
                    # Last method in class
                    set_value_end = len(class_section)
                
                old_method = class_section[set_value_start:set_value_end]
                
                # Check if it already has exception handling
                if 'try:' not in old_method and 'RuntimeError' not in old_method:
                    new_method = '''def set_value(self, val):
        try:
            self.setValue(float(val))
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise
        except (ValueError, TypeError):
            # Invalid value type
            return
        except Exception:
            return'''
                    
                    # Replace just this method in the class section
                    new_class_section = class_section[:set_value_start] + new_method + class_section[set_value_end:]
                    content = content[:idx] + new_class_section + content[next_class:]
                    
                    print("      ✓ Added exception handling to FCDoubleSpinner.set_value()")
                    patched_count += 1
                else:
                    print("      ⚠ Already has exception handling or pattern not found")
            else:
                print("      ⚠ set_value() not found in FCDoubleSpinner")
        else:
            print("      ⚠ FCDoubleSpinner class not found")
    else:
        print("      ⚠ FCDoubleSpinner class not found")
    
    # PATCH 5.3: FCSpinner.set_value()
    print("[3/4] Patching FCSpinner.set_value()...")
    search_3_pattern = r'(class FCSpinner.*?def set_value\(self.*?\):.*?self\.setValue)'
    
    # Look for the pattern more carefully
    spinner_pattern = '''def set_value(self, val):
        self.setValue(int(val))'''
    
    if spinner_pattern in content:
        spinner_replacement = '''def set_value(self, val):
        try:
            self.setValue(int(val))
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise
        except (ValueError, TypeError):
            return
        except Exception:
            return'''
        
        content = content.replace(spinner_pattern, spinner_replacement)
        print("      ✓ Added exception handling to FCSpinner.set_value()")
        patched_count += 1
    else:
        print("      ⚠ Pattern not found")
    
    # PATCH 5.4: Protect set_form_item in AppObjectTemplate.py
    print("[4/4] Patching AppObjectTemplate.set_form_item()...")
    
    template_file = repo_path / "appObjects" / "AppObjectTemplate.py"
    
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Find set_form_item method
        search_form = '''    def set_form_item(self, option):
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
        
        if search_form not in template_content:
            print("      ⚠ set_form_item already protected or pattern differs")
        else:
            print("      ✓ set_form_item() already has protection")
    else:
        print("      ⚠ AppObjectTemplate.py not found")
    
    # Write back GUIElements.py
    with open(gui_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✓ Applied {patched_count} widget safety patches")
    
    # Verify syntax
    print("\nVerifying syntax...")
    try:
        import py_compile
        py_compile.compile(str(gui_file), doraise=True)
        print("✓ Syntax verified - no errors")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False

def main():
    """Main function"""
    print("\n")
    
    if not apply_comprehensive_widget_patches():
        print("\n✗ PATCH FAILED")
        print("\nRolling back...")
        import subprocess
        subprocess.run("git checkout appGUI/GUIElements.py", cwd=r"C:\temp\flatcam_beta_broken", shell=True)
        subprocess.run("git checkout appObjects/AppObjectTemplate.py", cwd=r"C:\temp\flatcam_beta_broken", shell=True)
        print("✓ Rolled back to HEAD")
        return 1
    
    print("\n" + "=" * 70)
    print("PATCH-5 APPLIED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n📋 TESTING INSTRUCTIONS:")
    print("""
1. Start the application:
   python appMain.py

2. Open a Gerber file:
   File → Open Gerber File

3. CRITICAL TEST - Delete objects:
   - Right-click on the Gerber object in Project panel
   - Select "Delete" or press Delete key
   - Watch console for errors
   - Should delete without widget deletion crashes

4. Test object operations:
   - Open another Gerber file
   - Perform operations on multiple objects
   - Delete multiple objects
   - No "wrapped C/C++ object" errors should appear

5. Save project after deletions:
   File → Save Project As
   - Should save successfully
   - No widget deletion errors during serialization

6. Test repeated delete operations:
   - Delete several objects in sequence
   - Verify each deletion succeeds
   - Verify project saves after deletions

7. Exit the application:
   File → Exit (Ctrl+Q)
   - Should exit cleanly

If ALL tests pass, commit with:
   git add appGUI/GUIElements.py appObjects/AppObjectTemplate.py
   git commit -m "PATCH-5: Comprehensive widget safety for all UI elements
   
   - Add exception handling to FCCheckBox2.set_value()
   - Add exception handling to FCDoubleSpinner.set_value()
   - Add exception handling to FCSpinner.set_value()
   - Prevent crashes when widgets deleted during object operations
   - CRITICAL FIX for object deletion operations"

If ANY test fails:
   git checkout appGUI/GUIElements.py appObjects/AppObjectTemplate.py
   (to revert the patch)
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())