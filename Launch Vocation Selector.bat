@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 tools\vocation_selector_gui.py
  if %errorlevel%==0 exit /b 0
)
where python >nul 2>nul
if %errorlevel%==0 (
  python tools\vocation_selector_gui.py
  if %errorlevel%==0 exit /b 0
)
echo.
echo Python 3 with Tkinter is required for the experimental DQIX vocation selector.
echo Your files have not been changed.
echo Please install Python 3 from https://www.python.org/downloads/windows/
echo Then double-click this file again.
pause
exit /b 1
