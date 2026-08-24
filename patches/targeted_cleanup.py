#!/usr/bin/env python3
"""
Targeted cleanup - Remove only the three problem patch files and recover
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def main():
    """Main targeted cleanup function"""
    print("=" * 70)
    print("TARGETED CLEANUP - Remove Problem Patch Files")
    print("=" * 70)
    
    repo_path = Path(r"C:\temp\flatcam_beta_broken")
    
    if not repo_path.exists():
        print(f"✗ Repository not found: {repo_path}")
        return 1
    
    print(f"\nRepository: {repo_path}")
    
    # Step 1: Remove only the three problematic patch files
    print("\nStep 1: Removing problematic patch files...")
    
    files_to_remove = [
        "ultimate_widget_crash_fix.py",
        "fix_indentation_error.py",
        "ultimate_excellon_fix.py",
    ]
    
    for filename in files_to_remove:
        file_path = repo_path / filename
        if file_path.exists():
            file_path.unlink()
            print(f"  ✓ Removed {filename}")
        else:
            print(f"  ⚠ {filename} not found (already removed?)")
    
    # Step 2: Reset modified files to original state
    print("\nStep 2: Resetting modified files...")
    
    success, output = run_command("git reset --hard HEAD", cwd=str(repo_path))
    
    if success:
        print("  ✓ All tracked files reset to HEAD")
    else:
        print(f"  ✗ Error during reset: {output}")
        return 1
    
    # Step 3: Check git status
    print("\nStep 3: Checking git status...")
    
    success, output = run_command("git status --short", cwd=str(repo_path))
    
    if success:
        if output.strip():
            print("  Modified/untracked files:")
            print(output)
        else:
            print("  ✓ No modified files")
    
    # Step 4: Verify key files compile
    print("\nStep 4: Verifying key files compile...")
    
    key_files = [
        "appMain.py",
        "appGUI/GUIElements.py",
        "appObjects/ExcellonObject.py",
    ]
    
    all_ok = True
    for filename in key_files:
        file_path = repo_path / filename
        success, output = run_command(
            f"python -m py_compile {filename}",
            cwd=str(repo_path)
        )
        
        if success:
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename}: {output}")
            all_ok = False
    
    if not all_ok:
        print("\n✗ Some files have syntax errors")
        return 1
    
    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    
    print("\n✓ Problematic patch files removed")
    print("✓ Repository reset to clean state")
    print("✓ All key files verified")
    
    print("\nNext step:")
    print("  python appMain.py")
    print("\nIf the app starts, you have a clean baseline!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())