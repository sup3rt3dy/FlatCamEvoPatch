#!/bin/bash
# Git patch application script

cd /c/temp/flatcam_beta_broken

echo "Creating comprehensive patch..."

# Ensure we're on the right branch
git status

echo "Applying patches..."
python apply_patches.py

echo "Checking diff..."
git diff appMain.py | head -100

echo "Ready to commit?"
read -p "Press Enter to continue..."

git add appMain.py
git commit -m "Apply critical stability and performance improvements

- CRITICAL: Fix NoneType iteration in on_portable_checked()
- CRITICAL: Fix thread safety in quit_application()  
- CRITICAL: Fix hardcoded tab index bug
- HIGH: Add file resource management with context managers
- HIGH: Optimize message parsing with compiled regex
- HIGH: Improve pool memory management with timeout
- MEDIUM: Add null checks for threading objects
- MEDIUM: Better error logging and handling"

echo "Patches applied and committed!"