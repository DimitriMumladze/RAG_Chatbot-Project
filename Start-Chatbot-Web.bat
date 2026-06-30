@echo off
rem IBSU chatbot - web UI launcher. Double-click to run.
cd /d "%~dp0"
echo Starting IBSU chatbot (web UI)...
echo A browser tab will open at http://localhost:8501
echo Close this window to stop the chatbot.
call .\venv\Scripts\activate.bat
streamlit run app_streamlit.py
pause
