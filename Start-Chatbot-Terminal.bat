@echo off
rem IBSU chatbot - terminal chat launcher. Double-click to run.
cd /d "%~dp0"
echo Starting IBSU chatbot (terminal)...
call .\venv\Scripts\activate.bat
python app_cli.py
pause
