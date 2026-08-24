@echo off
REM FlatCAM appMain.py Patch Application Script for Windows
REM This script applies all critical stability and performance fixes

echo.
echo ===============================================================================
echo FlatCAM appMain.py - Comprehensive Stability Patch Application
echo ===============================================================================
echo.

setlocal enabledelayedexpansion

REM Set paths
set REPO_PATH=C:\temp\flatcam_beta_broken
set FILE_PATH=%REPO_PATH%\appMain.py
set BACKUP_PATH=%FILE_PATH%.backup
set TEMP_FILE=%FILE_PATH%.tmp

REM Check if file exists
if not exist "%FILE_PATH%" (
    echo Error: File not found: %FILE_PATH%
    exit /b 1
)

echo Target file: %FILE_PATH%
echo.

REM Create backup
if not exist "%BACKUP_PATH%" (
    copy "%FILE_PATH%" "%BACKUP_PATH%"
    echo Backup created: %BACKUP_PATH%
) else (
    echo Backup already exists: %BACKUP_PATH%
)

echo.
echo ===============================================================================
echo APPLYING PATCHES
echo ===============================================================================
echo.

echo Applying PATCH 1: Add compiled regex pattern...
echo PATCH 2: Use compiled regex in info() method...
echo PATCH 3: Fix hardcoded tab index...
echo PATCH 4: Fix on_portable_checked() method...
echo PATCH 5: Fix thread safety in quit_application()...
echo PATCH 6: Improve clear_pool() method...
echo.

REM Run Python script
python apply_patches.py
if errorlevel 1 (
    echo Error applying patches
    exit /b 1
)

echo.
echo ===============================================================================
echo PATCH APPLICATION COMPLETE
echo ===============================================================================
echo.
echo Next steps:
echo 1. Review changes: git diff appMain.py
echo 2. Test application: python appMain.py
echo 3. Commit changes: git add appMain.py ^&^& git commit -m "Apply stability patches"
echo 4. If needed, restore: copy "%BACKUP_PATH%" "%FILE_PATH%"
echo.

pause