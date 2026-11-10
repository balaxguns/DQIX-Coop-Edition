@echo off
setlocal
cd /d "%~dp0"
echo DQIX-Coop-Edition - SEPARATE playtest builder
echo.
echo Your existing Dragon Quest IX installation and save will not be modified.
echo This creates a new test folder from your own locally selected .nds ROM.
echo.
where py >nul 2>nul
if not errorlevel 1 (
    py -3 tools\build_playtest.py
    goto finish
)
where python >nul 2>nul
if not errorlevel 1 (
    python tools\build_playtest.py
    goto finish
)
echo Python 3 is required. Install it from https://www.python.org/downloads/windows/
:finish
echo.
pause
endlocal
