@echo off
cd /d "%~dp0"
if exist "FlowSync-AI\app.py" (
    cd FlowSync-AI
)
if not exist ".venv\Scripts\python.exe" (
    if exist "..\.venv\Scripts\python.exe" (
        call ..\.venv\Scripts\activate.bat
    ) else (
        py -m venv .venv
        call .venv\Scripts\activate.bat
    )
) else (
    call .venv\Scripts\activate.bat
)
python -m pip install -r requirements.txt
streamlit run app.py
pause
