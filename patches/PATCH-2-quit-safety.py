#!/usr/bin/env python3
"""
PATCH-2: Fix thread safety in quit_application()
Critical fix for safe application shutdown

Issue: self.new_launch and self.listen_th accessed without null checks
       Can cause AttributeError or RuntimeError on exit
Impact: App crashes on quit on Windows systems
Risk: LOW - Adds defensive checks only, doesn't change logic
"""

import sys
from pathlib import Path

def apply_patch():
    """Apply the quit_application thread safety patch"""
    print("=" * 70)
    print("PATCH-2: Fix quit_application() Thread Safety")
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
    
    # PATCH 2.1: Fix the new_launch.stop.emit() call
    search_pattern_1 = '''        if sys.platform == 'win32':
            self.new_launch.stop.emit()     # noqa
            # https://forum.qt.io/topic/108777/stop-a-loop-in-object-that-has-been-moved-to-a-qthread/7
            if self.listen_th.isRunning():
                self.listen_th.requestInterruption()
                self.log.debug("ArgThread QThread requested an interruption.")'''
    
    replacement_pattern_1 = '''        if sys.platform == 'win32':
            # CRITICAL FIX: Check if new_launch exists before calling stop
            try:
                if hasattr(self, 'new_launch') and self.new_launch is not None:
                    self.new_launch.stop.emit()     # noqa
            except Exception as e:
                if silent is False:
                    self.log.error("App.quit_application() --> Error stopping new_launch: %s" % str(e))

            # Check if listen_th exists and is running before requesting interruption
            try:
                if hasattr(self, 'listen_th') and self.listen_th is not None and self.listen_th.isRunning():
                    self.listen_th.requestInterruption()
                    if silent is False:
                        self.log.debug("ArgThread QThread requested an interruption.")
            except Exception as e:
                if silent is False:
                    self.log.error("App.quit_application() --> Error interrupting listen_th: %s" % str(e))'''
    
    if search_pattern_1 not in content:
        print("✗ Could not find pattern 1 (new_launch section)")
        return False
    
    print("✓ Found new_launch section")
    content = content.replace(search_pattern_1, replacement_pattern_1)
    print("  ✓ Added null checks for new_launch and listen_th")
    
    # PATCH 2.2: Fix the final thread cleanup
    search_pattern_2 = '''        # try to quit the QThread that run ArgsThread class
        try:
            # del self.new_launch
            if sys.platform == 'win32':
                self.listen_th.quit()
                self.listen_th.wait(1000)
        except Exception as e:
            if silent is False:
                self.log.error("App.quit_application() --> %s" % str(e))'''
    
    replacement_pattern_2 = '''        # try to quit the QThread that run ArgsThread class
        try:
            # del self.new_launch
            if sys.platform == 'win32':
                if hasattr(self, 'listen_th') and self.listen_th is not None:
                    self.listen_th.quit()
                    self.listen_th.wait(1000)
        except Exception as e:
            if silent is False:
                self.log.error("App.quit_application() --> %s" % str(e))'''
    
    if search_pattern_2 not in content:
        print("✗ Could not find pattern 2 (final cleanup)")
        return False
    
    print("✓ Found final cleanup section")
    content = content.replace(search_pattern_2, replacement_pattern_2)
    print("  ✓ Added null check for listen_th in final cleanup")
    
    # PATCH 2.3: Fix the close_command call
    search_pattern_3 = '''        QtWidgets.QApplication.quit()
        if sys.platform == 'win32':
            try:
                self.new_launch.close_command()
            except Exception:
                pass'''
    
    replacement_pattern_3 = '''        QtWidgets.QApplication.quit()
        if sys.platform == 'win32':
            try:
                if hasattr(self, 'new_launch') and self.new_launch is not None:
                    self.new_launch.close_command()
            except Exception:
                pass'''
    
    if search_pattern_3 not in content:
        print("✗ Could not find pattern 3 (close_command)")
        return False
    
    print("✓ Found close_command section")
    content = content.replace(search_pattern_3, replacement_pattern_3)
    print("  ✓ Added null check for new_launch.close_command()")
    
    # Write back
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ All three thread safety fixes applied")
    
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
    print("PATCH-2 APPLIED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n📋 TESTING INSTRUCTIONS:")
    print("""
1. Start the application:
   python appMain.py

2. Perform normal operations:
   - Open a file (Gerber, Excellon, or project)
   - Use some tools
   - Create/modify objects
   - This ensures the app is fully initialized

3. Exit the application:
   File → Exit (or Ctrl+Q)
   - Watch the console/terminal for errors
   - Should see clean shutdown with no exceptions
   - No "wrapped C/C++ object" errors
   - No AttributeError or RuntimeError

4. Repeat exit test 2-3 times:
   python appMain.py
   [use app briefly]
   Exit normally
   [repeat]

5. Check for success:
   - No error messages during shutdown
   - App closes cleanly
   - No lingering processes

If ALL tests pass, commit with:
   git add appMain.py
   git commit -m "PATCH-2: Add thread safety checks in quit_application()
   
   - Add null checks for new_launch before use
   - Add null checks for listen_th before use
   - Wrap thread operations in try/except blocks
   - Prevents AttributeError on Windows shutdown
   - CRITICAL FIX for safe application exit"

If ANY test fails:
   git checkout appMain.py
   (to revert the patch)
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())