#!/usr/bin/env python3
"""
PATCH-1: Fix NoneType iteration in on_portable_checked()
Critical fix for portable mode configuration handling

Issue: data can be None when file read fails, but code tries to loop through it
Impact: App crashes when toggling portable mode
Risk: LOW - Single method, defensive code only
"""

import sys
from pathlib import Path

def apply_patch():
    """Apply the portable check None handling patch"""
    print("=" * 70)
    print("PATCH-1: Fix on_portable_checked() None Check")
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
    
    # Find the on_portable_checked method
    search_pattern = '''        except FileNotFoundError:
            pass

        for line in data:'''
    
    # The fix - add a None check
    replacement_pattern = '''        except FileNotFoundError:
            self.log.warning('Configuration file not found at: %s' % config_file)
            return

        # CRITICAL FIX: Check if data is None before processing
        if data is None:
            self.log.error('App.on_portable_checked() --> Configuration data is None')
            return

        for line in data:'''
    
    if search_pattern not in content:
        print("✗ Could not find pattern in appMain.py")
        print("  Expected to find:")
        print("    except FileNotFoundError:")
        print("        pass")
        print("    ")
        print("    for line in data:")
        return False
    
    print("\n✓ Found on_portable_checked() method")
    
    # Apply the patch
    content = content.replace(search_pattern, replacement_pattern)
    
    # Write back
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Applied None check before data loop")
    
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
    print("PATCH-1 APPLIED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n📋 TESTING INSTRUCTIONS:")
    print("""
1. Start the application:
   python appMain.py

2. Open Edit → Preferences

3. Under General tab → Application Settings → "Portable Mode"
   - Toggle the checkbox ON and OFF several times
   - Watch for any error messages
   - Should NOT see RuntimeError or NoneType errors

4. Check logs for success:
   [DEBUG] App.on_portable_checked() --> Configuration data is None
   OR normal operation without errors

5. Close the app:
   File → Exit or Ctrl+Q

If ALL tests pass, commit with:
   git add appMain.py
   git commit -m "PATCH-1: Add None check in on_portable_checked()
   
   - Prevents NoneType iteration error
   - Safely handles missing configuration file
   - Logs warning when file not found
   - CRITICAL FIX for portable mode toggle"

If ANY test fails:
   git checkout appMain.py
   (to revert the patch)
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())