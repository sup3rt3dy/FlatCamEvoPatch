#!/usr/bin/env python3
"""
PATCH-8: Fix widget deletion errors in GerberObject.ui_disconnect()
Critical fix for UI cleanup safety

Issue: ui_disconnect() crashes when accessing deleted UI widgets
       Specifically: FCTable.rowCount() on deleted widget
Impact: Mirroring and other operations that call ui_disconnect fail
Risk: LOW - Exception handling only
"""

import sys
from pathlib import Path

def apply_patch():
    """Apply the GerberObject ui_disconnect safety patch"""
    print("=" * 70)
    print("PATCH-8: Fix GerberObject.ui_disconnect() Widget Safety")
    print("=" * 70)
    
    repo_path = Path(r"C:\temp\flatcam_beta_broken")
    gerber_file = repo_path / "appObjects" / "GerberObject.py"
    
    if not gerber_file.exists():
        print(f"✗ GerberObject.py not found: {gerber_file}")
        return False
    
    print(f"\nFile: {gerber_file}")
    
    # Read the file
    with open(gerber_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix ui_disconnect() method around line 395
    search_pattern = '''    def ui_disconnect(self):
        for row in range(self.ui.apertures_table.rowCount()):
            try:
                self.ui.apertures_table.cellWidget(row, 5).clicked.disconnect()
            except (TypeError, AttributeError):
                pass

        try:
            self.ui.mark_all_cb.clicked.disconnect(self.on_mark_all_click)
        except (TypeError, AttributeError):
            pass'''
    
    replacement_pattern = '''    def ui_disconnect(self):
        try:
            # Check if UI exists before accessing widgets
            if not hasattr(self, 'ui') or self.ui is None:
                return
            
            # Safely access apertures_table
            try:
                table = self.ui.apertures_table
                if table is not None:
                    for row in range(table.rowCount()):
                        try:
                            widget = table.cellWidget(row, 5)
                            if widget is not None:
                                widget.clicked.disconnect()
                        except (TypeError, AttributeError, RuntimeError):
                            pass
            except RuntimeError as e:
                # Widget has been deleted
                if "wrapped C/C++ object" in str(e):
                    pass
                else:
                    raise
            except (TypeError, AttributeError):
                pass

            # Safely disconnect mark_all_cb signal
            try:
                if hasattr(self.ui, 'mark_all_cb') and self.ui.mark_all_cb is not None:
                    self.ui.mark_all_cb.clicked.disconnect(self.on_mark_all_click)
            except (TypeError, AttributeError, RuntimeError):
                pass
        except Exception as e:
            # Log but don't crash on UI disconnect failures
            import logging
            logger = logging.getLogger('base')
            logger.debug(f"Error in ui_disconnect: {str(e)}")'''
    
    if search_pattern not in content:
        print("✗ Could not find ui_disconnect() pattern")
        return False
    
    print("✓ Found ui_disconnect() method")
    content = content.replace(search_pattern, replacement_pattern)
    print("  ✓ Added exception handling for widget deletion")
    print("  ✓ Added null checks for UI elements")
    
    # Write back
    with open(gerber_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ GerberObject safety patch applied")
    
    # Verify syntax
    print("\nVerifying syntax...")
    try:
        import py_compile
        py_compile.compile(str(gerber_file), doraise=True)
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
        subprocess.run("git checkout appObjects/GerberObject.py", cwd=r"C:\temp\flatcam_beta_broken", shell=True)
        print("✓ Rolled back to HEAD")
        return 1
    
    print("\n" + "=" * 70)
    print("PATCH-8 APPLIED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n📋 TESTING INSTRUCTIONS:")
    print("""
1. Start the application:
   python appMain.py

2. Open a Gerber file:
   File → Open Gerber File

3. CRITICAL TEST - Use Double Sided Tool:
   - Go to Tools → Double Sided
   - Select the Gerber object
   - Click "Mirror" button
   - Watch console for errors
   - Should work without widget deletion errors

4. Test other operations:
   - Open another Gerber
   - Try mirroring again
   - Try other transformations
   - Should be stable

5. Test object deletion:
   - Delete objects during/after operations
   - No crashes should occur

6. Exit the application:
   File → Exit (Ctrl+Q)

If ALL tests pass, commit with:
   git add appObjects/GerberObject.py
   git commit -m "PATCH-8: Fix ui_disconnect() widget deletion safety
   
   - Add null checks for UI existence
   - Safely handle deleted widget access
   - Catch RuntimeError for deleted FCTable
   - Check widget existence before operations
   - CRITICAL FIX for mirror/transform operations"

If ANY test fails:
   git checkout appObjects/GerberObject.py
   (to revert the patch)
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())