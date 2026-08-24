#!/usr/bin/env python3
"""
PATCH-6: Fix signal disconnection on deleted widgets
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
    print("PATCH-6: Fix Signal Disconnection on Deleted Widgets")
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
    
    # Find and fix the disable_plots method around line 7517
    search_pattern = '''    def disable_plots(self, objects=None):
        """
        Disables the plots for the given objects. If the objects list is empty
        will disable the plots for all objects.

        :param objects: list of objects to disable plot
        :type objects: list or None
        :return: None
        """

        if not objects:
            objects = self.collection.get_list()

        for obj in objects:
            if obj is None:
                continue
            obj.ui.plot_cb.stateChanged.disconnect(obj.on_plot_cb_click)
            obj.plot_cb_disconnect = True
            obj.ui.plot_cb.setCheckState(QtCore.Qt.CheckState.Unchecked)
            obj.ui.plot_cb.stateChanged.connect(obj.on_plot_cb_click)'''
    
    replacement_pattern = '''    def disable_plots(self, objects=None):
        """
        Disables the plots for the given objects. If the objects list is empty
        will disable the plots for all objects.

        :param objects: list of objects to disable plot
        :type objects: list or None
        :return: None
        """

        if not objects:
            objects = self.collection.get_list()

        for obj in objects:
            if obj is None:
                continue
            try:
                # Safely disconnect signal from widget that may have been deleted
                if hasattr(obj, 'ui') and obj.ui is not None and hasattr(obj.ui, 'plot_cb'):
                    if obj.ui.plot_cb is not None:
                        try:
                            obj.ui.plot_cb.stateChanged.disconnect(obj.on_plot_cb_click)
                        except RuntimeError:
                            # Widget already deleted, skip disconnect
                            pass
            except Exception as e:
                self.log.debug(f"Error disconnecting plot_cb signal: {str(e)}")
            
            obj.plot_cb_disconnect = True
            
            try:
                if hasattr(obj, 'ui') and obj.ui is not None and hasattr(obj.ui, 'plot_cb'):
                    if obj.ui.plot_cb is not None:
                        obj.ui.plot_cb.setCheckState(QtCore.Qt.CheckState.Unchecked)
            except RuntimeError:
                # Widget deleted, skip state change
                pass
            
            try:
                if hasattr(obj, 'ui') and obj.ui is not None and hasattr(obj.ui, 'plot_cb'):
                    if obj.ui.plot_cb is not None:
                        obj.ui.plot_cb.stateChanged.connect(obj.on_plot_cb_click)
            except RuntimeError:
                # Widget deleted, skip reconnect
                pass'''
    
    if search_pattern not in content:
        print("✗ Could not find disable_plots pattern")
        return False
    
    print("✓ Found disable_plots method")
    content = content.replace(search_pattern, replacement_pattern)
    print("  ✓ Added exception handling for signal disconnection")
    
    # Also find and fix enable_plots method
    search_pattern2 = '''    def enable_plots(self, objects=None):
        """
        Enables the plots for the given objects. If the objects list is empty
        will enable the plots for all objects.

        :param objects: list of objects to enable plot
        :type objects: list or None
        :return: None
        """

        if not objects:
            objects = self.collection.get_list()

        for obj in objects:
            if obj is None:
                continue
            obj.ui.plot_cb.stateChanged.disconnect(obj.on_plot_cb_click)
            obj.plot_cb_disconnect = True
            obj.ui.plot_cb.setCheckState(QtCore.Qt.CheckState.Checked)
            obj.ui.plot_cb.stateChanged.connect(obj.on_plot_cb_click)'''
    
    replacement_pattern2 = '''    def enable_plots(self, objects=None):
        """
        Enables the plots for the given objects. If the objects list is empty
        will enable the plots for all objects.

        :param objects: list of objects to enable plot
        :type objects: list or None
        :return: None
        """

        if not objects:
            objects = self.collection.get_list()

        for obj in objects:
            if obj is None:
                continue
            try:
                # Safely disconnect signal from widget that may have been deleted
                if hasattr(obj, 'ui') and obj.ui is not None and hasattr(obj.ui, 'plot_cb'):
                    if obj.ui.plot_cb is not None:
                        try:
                            obj.ui.plot_cb.stateChanged.disconnect(obj.on_plot_cb_click)
                        except RuntimeError:
                            # Widget already deleted, skip disconnect
                            pass
            except Exception as e:
                self.log.debug(f"Error disconnecting plot_cb signal: {str(e)}")
            
            obj.plot_cb_disconnect = True
            
            try:
                if hasattr(obj, 'ui') and obj.ui is not None and hasattr(obj.ui, 'plot_cb'):
                    if obj.ui.plot_cb is not None:
                        obj.ui.plot_cb.setCheckState(QtCore.Qt.CheckState.Checked)
            except RuntimeError:
                # Widget deleted, skip state change
                pass
            
            try:
                if hasattr(obj, 'ui') and obj.ui is not None and hasattr(obj.ui, 'plot_cb'):
                    if obj.ui.plot_cb is not None:
                        obj.ui.plot_cb.stateChanged.connect(obj.on_plot_cb_click)
            except RuntimeError:
                # Widget deleted, skip reconnect
                pass'''
    
    if search_pattern2 in content:
        print("✓ Found enable_plots method")
        content = content.replace(search_pattern2, replacement_pattern2)
        print("  ✓ Added exception handling to enable_plots as well")
    else:
        print("⚠ Could not find enable_plots method (may be different)")
    
    # Write back
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ Signal safety patches applied")
    
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
    print("PATCH-6 APPLIED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n📋 TESTING INSTRUCTIONS:")
    print("""
1. Start the application:
   python appMain.py

2. Open a Gerber file:
   File → Open Gerber File

3. CRITICAL TEST - Disable/Enable plots:
   - Right-click on the object in Project panel
   - Select "Disable" (or "Enable")
   - Watch console for errors
   - Should work without widget deletion errors

4. Test multiple times:
   - Disable multiple objects
   - Enable multiple objects
   - Mix of disable/enable operations
   - No "wrapped C/C++ object" errors should appear

5. Test with deleted objects:
   - Delete one object
   - Disable/enable remaining objects
   - Should work smoothly

6. Exit the application:
   File → Exit (Ctrl+Q)
   - Should exit cleanly

If ALL tests pass, commit with:
   git add appMain.py
   git commit -m "PATCH-6: Fix signal disconnection on deleted widgets
   
   - Add exception handling to disable_plots()
   - Add exception handling to enable_plots()
   - Safely handle signal disconnect on deleted widgets
   - Check widget existence before signal operations
   - CRITICAL FIX for plot enable/disable operations"

If ANY test fails:
   git checkout appMain.py
   (to revert the patch)
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())