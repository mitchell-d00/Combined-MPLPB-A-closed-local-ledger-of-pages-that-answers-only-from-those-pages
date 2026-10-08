@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 launch.py %*
) else (
    python launch.py %*
)
if errorlevel 1 (
    echo Launch failed. Check the error above. Python 3 is required.
    echo Read docs\BROWSER_UI.md for instructions.
    pause
)
