@echo off
echo Checking Ollama Installation...
echo.

where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Ollama is NOT installed or not in your PATH.
    echo Please install it from https://ollama.com/download
    echo.
    pause
    exit /b 1
)

echo [OK] Ollama is installed.
echo Checking for llama3 model...
echo.

ollama list | findstr "llama3" >nul
if %errorlevel% neq 0 (
    echo [WARNING] llama3 model not found.
    echo Downloading llama3 now...
    ollama pull llama3
) else (
    echo [OK] llama3 model is ready.
)

echo.
echo All checks passed! The Varma System should work now.
pause
