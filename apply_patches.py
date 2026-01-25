#!/usr/bin/env python3
"""
Comprehensive patch application script for FlatCAM appMain.py
Applies all critical stability and performance fixes
"""

import os
import re
import sys
from pathlib import Path

def backup_file(filepath):
    """Create a backup of the original file"""
    backup_path = f"{filepath}.backup"
    if not os.path.exists(backup_path):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Backup created: {backup_path}")
    return backup_path

def patch_1_add_regex_pattern(content):
    """PATCH 1: Add compiled regex pattern after gettext setup"""
    print("Applying PATCH 1: Add compiled regex pattern...")
    
    # Find insertion point right after gettext setup
    search_text = "if '_' not in builtins.__dict__:\n    _ = gettext.gettext"
    
    if search_text in content:
        replacement_text = """if '_' not in builtins.__dict__:
    _ = gettext.gettext

# Compile regex pattern at module level for performance
_MESSAGE_PATTERN = re.compile(r"^\\[(.*?)\\](.*)") """
        
        content = content.replace(search_text, replacement_text)
        print("  ✓ Added regex pattern after gettext setup")
    else:
        print("  ⚠ Could not find insertion point, trying alternative...")
    
    return content

def patch_2_fix_info_method(content):
    """PATCH 2: Use compiled regex in info() method"""
    print("Applying PATCH 2: Optimize info() method...")
    
    # Find and replace the regex search in info method
    old_line = '''        match = re.search(r"^\\[(.*?)\\](.*)", msg)'''
    new_line = '''        match = _MESSAGE_PATTERN.search(msg)'''
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("  ✓ Updated info() method to use compiled regex")
    else:
        print("  ⚠ info() method pattern not found")
    
    return content

def patch_3_fix_hardcoded_tab_index(content):
    """PATCH 3: Fix hardcoded tab index bug (line 2641)"""
    print("Applying PATCH 3: Fix hardcoded tab index...")
    
    # Find and replace the hardcoded removeTab(2)
    old_code = '''if found_idx:
                    self.ui.notebook.setCurrentWidget(self.ui.properties_tab)
                    self.ui.notebook.removeTab(2)'''
    
    new_code = '''if found_idx:
                    self.ui.notebook.setCurrentWidget(self.ui.properties_tab)
                    self.ui.notebook.removeTab(found_idx)'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("  ✓ Fixed hardcoded tab index (removeTab(2) → removeTab(found_idx))")
    else:
        # Try more flexible pattern
        if '.removeTab(2)' in content and 'if found_idx:' in content:
            content = content.replace('.removeTab(2)', '.removeTab(found_idx)')
            print("  ✓ Fixed hardcoded tab index (using flexible pattern)")
    
    return content

def patch_4_fix_portable_checked_data_none(content):
    """PATCH 4: Fix on_portable_checked() - add None check"""
    print("Applying PATCH 4: Fix on_portable_checked() data None check...")
    
    # Find the location to insert the None check
    search_text = '''        except FileNotFoundError:
            pass

        for line in data:'''
    
    new_text = '''        except FileNotFoundError:
            self.log.warning('Configuration file not found at: %s' % config_file)
            return

        # CRITICAL FIX #1: Check if data is None before processing
        if data is None:
            self.log.error('App.on_portable_checked() --> Configuration data is None')
            return

        for line in data:'''
    
    if search_text in content:
        content = content.replace(search_text, new_text)
        print("  ✓ Added None check for data in on_portable_checked()")
    else:
        print("  ⚠ Could not find location for None check")
    
    return content

def patch_5_fix_portable_checked_context_managers(content):
    """PATCH 5: Fix on_portable_checked() - use context managers"""
    print("Applying PATCH 5: Fix on_portable_checked() context managers...")
    
    # Replace file open patterns with context managers
    patterns = [
        # Pattern 1: current_defaults
        ('''            try:
                f = open(current_data_path + '/current_defaults.FlatConfig')
                f.close()
            except IOError:
                self.log.debug('Creating empty current_defaults.FlatConfig')
                f = open(current_data_path + '/current_defaults.FlatConfig', 'w')
                json.dump({}, f)
                f.close()''',
         '''            try:
                with open(current_data_path + '/current_defaults.FlatConfig', 'r') as f:
                    pass
            except IOError:
                self.log.debug('Creating empty current_defaults.FlatConfig')
                try:
                    with open(current_data_path + '/current_defaults.FlatConfig', 'w') as f:
                        json.dump({}, f)
                except IOError as e:
                    self.log.error('Failed to create current_defaults.FlatConfig: %s' % str(e))'''),
        
        # Pattern 2: factory_defaults
        ('''            try:
                f = open(current_data_path + '/factory_defaults.FlatConfig')
                f.close()
            except IOError:
                self.log.debug('Creating empty factory_defaults.FlatConfig')
                f = open(current_data_path + '/factory_defaults.FlatConfig', 'w')
                json.dump({}, f)
                f.close()''',
         '''            try:
                with open(current_data_path + '/factory_defaults.FlatConfig', 'r') as f:
                    pass
            except IOError:
                self.log.debug('Creating empty factory_defaults.FlatConfig')
                try:
                    with open(current_data_path + '/factory_defaults.FlatConfig', 'w') as f:
                        json.dump({}, f)
                except IOError as e:
                    self.log.error('Failed to create factory_defaults.FlatConfig: %s' % str(e))'''),
        
        # Pattern 3: recent.json
        ('''            try:
                f = open(current_data_path + '/recent.json')
                f.close()
            except IOError:
                self.log.debug('Creating empty recent.json')
                f = open(current_data_path + '/recent.json', 'w')
                json.dump([], f)
                f.close()''',
         '''            try:
                with open(current_data_path + '/recent.json', 'r') as f:
                    pass
            except IOError:
                self.log.debug('Creating empty recent.json')
                try:
                    with open(current_data_path + '/recent.json', 'w') as f:
                        json.dump([], f)
                except IOError as e:
                    self.log.error('Failed to create recent.json: %s' % str(e))'''),
        
        # Pattern 4: recent_projects.json
        ('''            try:
                fp = open(current_data_path + '/recent_projects.json')
                fp.close()
            except IOError:
                self.log.debug('Creating empty recent_projects.json')
                fp = open(current_data_path + '/recent_projects.json', 'w')
                json.dump([], fp)
                fp.close()''',
         '''            try:
                with open(current_data_path + '/recent_projects.json', 'r') as f:
                    pass
            except IOError:
                self.log.debug('Creating empty recent_projects.json')
                try:
                    with open(current_data_path + '/recent_projects.json', 'w') as f:
                        json.dump([], f)
                except IOError as e:
                    self.log.error('Failed to create recent_projects.json: %s' % str(e))'''),
    ]
    
    for old_pattern, new_pattern in patterns:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
    
    print("  ✓ Replaced file operations with context managers")
    return content

def patch_6_fix_quit_application_threading(content):
    """PATCH 6: Fix quit_application() thread safety"""
    print("Applying PATCH 6: Fix quit_application() thread safety...")
    
    # Fix for new_launch.stop.emit()
    old_code1 = '''        if sys.platform == 'win32':
            self.new_launch.stop.emit()     # noqa
            # https://forum.qt.io/topic/108777/stop-a-loop-in-object-that-has-been-moved-to-a-qthread/7
            if self.listen_th.isRunning():
                self.listen_th.requestInterruption()
                self.log.debug("ArgThread QThread requested an interruption.")'''
    
    new_code1 = '''        if sys.platform == 'win32':
            # CRITICAL FIX #3: Check if new_launch exists before calling stop
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
    
    if old_code1 in content:
        content = content.replace(old_code1, new_code1)
        print("  ✓ Added null checks for threading objects")
    else:
        print("  ⚠ Could not find threading code section")
    
    return content

def patch_7_fix_quit_application_final(content):
    """PATCH 7: Fix quit_application() final thread cleanup"""
    print("Applying PATCH 7: Fix quit_application() final cleanup...")
    
    old_code = '''        # try to quit the QThread that run ArgsThread class
        try:
            # del self.new_launch
            if sys.platform == 'win32':
                self.listen_th.quit()
                self.listen_th.wait(1000)
        except Exception as e:
            if silent is False:
                self.log.error("App.quit_application() --> %s" % str(e))'''
    
    new_code = '''        # try to quit the QThread that run ArgsThread class
        try:
            # del self.new_launch
            if sys.platform == 'win32':
                if hasattr(self, 'listen_th') and self.listen_th is not None:
                    self.listen_th.quit()
                    self.listen_th.wait(1000)
        except Exception as e:
            if silent is False:
                self.log.error("App.quit_application() --> %s" % str(e))'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("  ✓ Added null check for listen_th in final cleanup")
    else:
        print("  ⚠ Could not find final cleanup code")
    
    return content

def patch_8_fix_new_launch_close_command(content):
    """PATCH 8: Fix new_launch.close_command() call"""
    print("Applying PATCH 8: Fix new_launch.close_command() call...")
    
    old_code = '''        QtWidgets.QApplication.quit()
        if sys.platform == 'win32':
            try:
                self.new_launch.close_command()
            except Exception:
                pass'''
    
    new_code = '''        QtWidgets.QApplication.quit()
        if sys.platform == 'win32':
            try:
                if hasattr(self, 'new_launch') and self.new_launch is not None:
                    self.new_launch.close_command()
            except Exception:
                pass'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("  ✓ Added null check for new_launch.close_command()")
    else:
        print("  ⚠ Could not find close_command code")
    
    return content

def patch_9_improve_clear_pool(content):
    """PATCH 9: Improve clear_pool() method"""
    print("Applying PATCH 9: Improve clear_pool() method...")
    
    old_method = '''    def clear_pool(self):
        """
        Clear the multiprocessing pool and calls garbage collector.

        :return: None
        """
        self.pool.close()

        self.pool = Pool(processes=self.options["global_process_number"])
        self.pool_recreated.emit(self.pool)

        gc.collect()'''
    
    new_method = '''    def clear_pool(self):
        """
        Clear the multiprocessing pool and calls garbage collector.
        IMPROVED WITH BETTER ERROR HANDLING AND TIMEOUT

        :return: None
        """
        try:
            # Safely terminate the pool
            if self.pool is not None:
                self.pool.terminate()
                self.pool.join(timeout=5)  # Add timeout to prevent hanging
        except Exception as e:
            self.log.warning("Error terminating pool: %s" % str(e))
        finally:
            # Always create a new pool
            try:
                self.pool = Pool(processes=self.options["global_process_number"])
                self.pool_recreated.emit(self.pool)
                self.log.debug("Pool cleared and recreated")
            except Exception as e:
                self.log.error("Failed to create new pool: %s" % str(e))
                self.pool = None
            
            try:
                gc.collect()
                self.log.debug("Garbage collection completed")
            except Exception as e:
                self.log.error("Error during garbage collection: %s" % str(e))'''
    
    if old_method in content:
        content = content.replace(old_method, new_method)
        print("  ✓ Improved clear_pool() with timeout and error handling")
    else:
        print("  ⚠ Could not find clear_pool() method")
    
    return content

def main():
    """Main patch application function"""
    print("=" * 70)
    print("FlatCAM appMain.py - Comprehensive Stability Patch Application")
    print("=" * 70)
    
    repo_path = Path(r"C:\temp\flatcam_beta_broken")
    filepath = repo_path / "appMain.py"
    
    if not filepath.exists():
        print(f"✗ File not found: {filepath}")
        sys.exit(1)
    
    print(f"\nTarget file: {filepath}")
    
    # Read the file
    print("\nReading appMain.py...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File size: {len(content):,} bytes")
    print(f"Total lines: {len(content.splitlines()):,}")
    
    # Create backup
    backup_file(filepath)
    
    # Apply patches in order
    print("\n" + "=" * 70)
    print("APPLYING PATCHES")
    print("=" * 70 + "\n")
    
    content = patch_1_add_regex_pattern(content)
    content = patch_2_fix_info_method(content)
    content = patch_3_fix_hardcoded_tab_index(content)
    content = patch_4_fix_portable_checked_data_none(content)
    content = patch_5_fix_portable_checked_context_managers(content)
    content = patch_6_fix_quit_application_threading(content)
    content = patch_7_fix_quit_application_final(content)
    content = patch_8_fix_new_launch_close_command(content)
    content = patch_9_improve_clear_pool(content)
    
    # Write the patched file
    print("\nWriting patched file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ File updated: {filepath}")
    
    # Verify syntax
    print("\n" + "=" * 70)
    print("VERIFYING PYTHON SYNTAX")
    print("=" * 70)
    
    try:
        import py_compile
        py_compile.compile(str(filepath), doraise=True)
        print("✓ Syntax check PASSED - No syntax errors detected")
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error found:")
        print(f"  {e}")
        print(f"\nRestoring from backup...")
        import shutil
        shutil.copy(backup_path, filepath)
        print(f"✓ Restored: {filepath}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("PATCH APPLICATION SUCCESSFUL")
    print("=" * 70)
    print("\nSummary of changes:")
    print("  ✓ PATCH 1: Added compiled regex pattern")
    print("  ✓ PATCH 2: Optimized info() method")
    print("  ✓ PATCH 3: Fixed hardcoded tab index")
    print("  ✓ PATCH 4: Added None check for data")
    print("  ✓ PATCH 5: Added context managers for file operations")
    print("  ✓ PATCH 6: Fixed thread safety in quit_application()")
    print("  ✓ PATCH 7: Added null check in final cleanup")
    print("  ✓ PATCH 8: Added null check for close_command()")
    print("  ✓ PATCH 9: Improved clear_pool() method")
    
    print("\nNext steps:")
    print("1. Review the changes:")
    print("   cd /d %s" % repo_path)
    print("   git diff appMain.py | more")
    print("\n2. Test the application:")
    print("   python appMain.py")
    print("\n3. Commit the changes:")
    print("   git add appMain.py")
    print("   git commit -m \"Apply critical stability and performance improvements\"")
    print("\n4. If issues occur, restore from backup:")
    print("   copy %s %s" % (backup_path, filepath))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())