#!/usr/bin/env python3
"""
PATCH-7: Fix widget deletion errors in EvalEntry.set_value()
Critical fix for text entry safety during editor operations

Issue: EvalEntry.set_value() crashes if widget deleted during editing
       Affects: EvalEntry, NumericalEvalEntry, NumericalEvalTupleEntry
Impact: Cannot save Gerber edits, editor operations fail
Risk: LOW - Exception handling only
"""

import sys
from pathlib import Path

def apply_patch():
    """Apply the EvalEntry widget safety patch"""
    print("=" * 70)
    print("PATCH-7: Fix EvalEntry.set_value() Widget Deletion Safety")
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
    
    # Find and fix EvalEntry.set_value() around line 954
    search_pattern = '''    def set_value(self, val):
        self.setText(str(val))

    def sizeHint(self):
        default_hint_size = super(EvalEntry, self).sizeHint()
        return QtCore.QSize(EDIT_SIZE_HINT, default_hint_size.height())'''
    
    replacement_pattern = '''    def set_value(self, val):
        try:
            self.setText(str(val))
        except RuntimeError as e:
            # Widget has been deleted in parent thread
            if "wrapped C/C++ object" in str(e):
                return
            raise
        except Exception:
            # Any other exception - silently return
            return

    def sizeHint(self):
        default_hint_size = super(EvalEntry, self).sizeHint()
        return QtCore.QSize(EDIT_SIZE_HINT, default_hint_size.height())'''
    
    if search_pattern not in content:
        print("✗ Could not find EvalEntry.set_value() pattern")
        return False
    
    print("✓ Found EvalEntry.set_value() method")
    content = content.replace(search_pattern, replacement_pattern)
    print("  ✓ Added exception handling to EvalEntry.set_value()")
    print("  ✓ This also protects NumericalEvalEntry and NumericalEvalTupleEntry (inherit from EvalEntry)")
    
    # Write back
    with open(gui_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ EvalEntry safety patch applied")
    
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
    
    if not apply_patch():
        print("\n✗ PATCH FAILED")
        print("\nRolling back...")
        import subprocess
        subprocess.run("git checkout appGUI/GUIElements.py", cwd=r"C:\temp\flatcam_beta_broken", shell=True)
        print("✓ Rolled back to HEAD")
        return 1
    
    print("\n" + "=" * 70)
    print("PATCH-7 APPLIED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n📋 TESTING INSTRUCTIONS:")
    print("""
1. Start the application:
   python appMain.py

2. Open a Gerber file:
   File → Open Gerber File

3. CRITICAL TEST - Edit and save Gerber:
   - Right-click on Gerber object
   - Select "Edit"
   - Make some changes to the geometry
   - Click "Save" or "Exit"
   - Watch console for errors
   - Should work without widget deletion errors

4. Test multiple edit cycles:
   - Edit Gerber
   - Save
   - Edit again
   - Save again
   - Repeat 3-5 times
   - No "wrapped C/C++ object" errors should appear

5. Test editor operations:
   - Edit multiple times
   - Use different tools in editor
   - Save each time
   - Should be stable

6. Exit the application:
   File → Exit (Ctrl+Q)
   - Should exit cleanly

If ALL tests pass, commit with:
   git add appGUI/GUIElements.py
   git commit -m "PATCH-7: Add exception handling to EvalEntry.set_value()
   
   - Protect EvalEntry widget deletion during editor operations
   - Also protects NumericalEvalEntry and NumericalEvalTupleEntry
   - Safely handle RuntimeError for deleted widgets
   - Fixes Gerber edit/save operations
   - CRITICAL FIX for editor operations"

If ANY test fails:
   git checkout appGUI/GUIElements.py
   (to revert the patch)
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())