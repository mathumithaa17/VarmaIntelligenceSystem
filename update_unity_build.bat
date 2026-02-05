@echo off
echo ===================================================
echo Syncing Unity Build Files to Web Public Folder
echo ===================================================

set "SOURCE_DIR=Varma-Unity-main (2)\Varma-Unity-main\buildFolder\Build"
set "DEST_DIR=varma-intelligence-system\public\Web_text\Build"

echo Source: %SOURCE_DIR%
echo Dest:   %DEST_DIR%

if not exist "%SOURCE_DIR%" (
    echo [ERROR] Source directory not found!
    echo Checked: %SOURCE_DIR%
    pause
    exit /b 1
)

if not exist "%DEST_DIR%" (
    echo [INFO] Destination directory does not exist. Creating it...
    mkdir "%DEST_DIR%"
)

echo.
echo Copying files...
xcopy /Y /S /I "%SOURCE_DIR%\*.*" "%DEST_DIR%\"

if %errorlevel% neq 0 (
    echo [ERROR] Failed to satisfy copy command.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Unity build files updated successfully!
echo.
echo IMPORTANT: Now you must run these commands to push the files:
echo 1. git add varma-intelligence-system/public/Web_text/Build/
echo 2. git commit -m "Update Unity build files"
echo 3. git push
echo.
pause
