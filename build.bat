@echo off
:: Move to the folder where this bat lives (fixes "do not run from System32" error)
cd /d "%~dp0"
echo ============================================
echo  SYSMON -- Build Script
echo ============================================

:: Install / upgrade dependencies
echo [1/3] Installing Python dependencies...
pip install fastapi uvicorn psutil pystray Pillow pyinstaller --upgrade --quiet
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause & exit /b 1
)

:: Clean previous build
echo [2/3] Cleaning previous build...
if exist dist\SYSMON.exe del /f dist\SYSMON.exe
if exist build rmdir /s /q build

:: Build with PyInstaller
echo [3/3] Building SYSMON.exe...
pyinstaller sysmon.spec --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause & exit /b 1
)

echo.
echo ============================================
echo  Build complete: dist\SYSMON.exe
echo ============================================
pause
