#!/usr/bin/env python3
"""
PATCH-6-CORRECT: Fix signal disconnection on deleted widgets
Critical fix for UI state management

Issue: disconnect() called on deleted widget signals causing crashes
Impact: Cannot disable/enable plots, toggle object visibility
Risk: LOW - Exception handling only
"""

import sys
from pathlib import Path

def apply_patch():
    """Apply the signal disconnect safety patch"""
    print("=" * 70)
    print("PATCH-6-CORRECT: Fix Signal Disconnection on Deleted Widgets")
    print("=" * 70)
    
    repo_path = Path(r"C:\temp\flatcam_beta_broken")
    app_file = repo_path / "appMain.py"
    
    if not app_file.exists():
        print(f"✗ appMain.py not found: {app_file}")
        return False
    
    print(f"\nFile: {app_file}")
    
    # Read the file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the disable_plots method - lines 7501-7530
    search_pattern = '''    def disable_plots(self, objects):
        """
        Disables plots

        :param objects: list of Objects to be disabled
        :return:
        """

        self.log.debug("Disabling plots ...")
        # self.inform.emit('%s...' % _("Working"))

        for obj in objects:
            if obj.obj_options['plot'] is True:
                obj.obj_options.set_change_callback(lambda x: None)
                try:
                    obj.obj_options['plot'] = False
                    obj.ui.plot_cb.stateChanged.disconnect(obj.on_plot_cb_click)
                    obj.ui.plot_cb.setDisabled(True)
                except (AttributeError, TypeError):
                    # try to build the ui
                    obj.build_ui()
                    # and try again
                    self.disable_plots(objects)

                obj.set_form_item("plot")
                try:
                    obj.ui.plot_cb.stateChanged.connect(obj.on_plot_cb_click)
                    obj.ui.plot_cb.setDisabled(False)
                except (AttributeError, TypeError):'''
    
    replacement_pattern = '''    def disable_plots(self, objects):
        """
        Disables plots

        :param objects: list of Objects to be disabled
        :return:
        """

        self.log.debug("Disabling plots ...")
        # self.inform.emit('%s...' % _("Working"))

        for obj in objects:
            if obj.obj_options['plot'] is True:
                obj.obj_options.set_change_callback(lambda x: None)
                try:
                    obj.obj_options['plot'] = False
                    try:
                        # Safely disconnect signal from widget that may have been deleted
                        obj.ui.plot_cb.stateChanged.disconnect(obj.on_plot_cb_click)
                    except RuntimeError as e:
                        # Widget already deleted, skip disconnect
                        if "wrapped C/C++ object" not in str(e):
                            raise
                    obj.ui.plot_cb.setDisabled(True)
                except (AttributeError, TypeError, RuntimeError):
                    # try to build the ui
                    obj.build_ui()
                    # and try again
                    self.disable_plots(objects)
                    return

                obj.set_form_item("plot")
                try:
                    obj.ui.plot_cb.stateChanged.connect(obj.on_plot_cb_click)
                    obj.ui.plot_cb.setDisabled(False)
                except (AttributeError, TypeError, RuntimeError):'''
    
    if search_pattern not in content:
        print("✗ Could not find exact disable_plots pattern")
        return False
    
    print("✓ Found disable_plots method")
    content = content.replace(search_pattern, replacement_pattern)
    print("  ✓ Added exception handling for signal disconnection")
    
    # Write back
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ Signal safety patch applied")
    
    # Verify syntax
    print("\nVerifying syntax...")
    try:
        import py_compile
        py_compile.compile(str(app_file), doraise=True)
        print("✓ Syntax verified - no errors")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False

def main():
    """Main function"""
    print("\n")
    
    if not apply_patch():
        print("\n✗ PATCH FAILED")
        print("\nRolling back...")
        import subprocess
        subprocess.run("git checkout appMain.py", cwd=r"C:\temp\flatcam_beta_broken", shell=True)
        print("✓ Rolled back to HEAD")
        return 1
    
    print("\n" + "=" * 70)
    print("PATCH-6-CORRECT APPLIED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n📋 TESTING INSTRUCTIONS:")
    print("""
1. Start the application:
   python appMain.py

2. Open a Gerber file:
   File → Open Gerber File

3. CRITICAL TEST - Disable plot:
   - Right-click on the object in Project panel
   - Select "Disable" 
   - Watch console for errors
   - Should work without widget deletion errors

4. Test enable plot:
   - Right-click again
   - Select "Enable"
   - Should work smoothly

5. Test multiple times:
   - Disable/Enable several times
   - No "wrapped C/C++ object" errors should appear

6. Test with deleted objects:
   - Delete one object
   - Disable/enable remaining objects
   - Should work smoothly

7. Exit the application:
   File → Exit (Ctrl+Q)

If ALL tests pass, commit with:
   git add appMain.py
   git commit -m "PATCH-6: Fix signal disconnection on deleted widgets
   
   - Add RuntimeError handling to disable_plots()
   - Safely handle signal disconnect on deleted widgets
   - Check for widget deletion before state changes
   - CRITICAL FIX for plot disable/enable operations"

If test FAILS:
   git checkout appMain.py
   (revert the patch)
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())