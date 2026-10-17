@echo off
cd /d "%~dp0"
python main.py
if errorlevel 1 (
  echo.
  echo SahakarSeva could not start. Read the message above.
  pause
)
