@echo off
cd /d "%~dp0" || exit /b
python -m venv .venv || exit /b
call .\.venv\Scripts\activate || exit /b
pip install -r requirements.txt || exit /b
streamlit run app.py || exit /b
deactivate
pause
