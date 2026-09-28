@echo off
cd /d "%~dp0"
if exist .env for /f "usebackq tokens=1,* delims==" %%A in (".env") do if not "%%A"=="" set "%%A=%%B"
if "%ANTHROPIC_API_KEY%"=="" (echo Set ANTHROPIC_API_KEY in .env & exit /b 1)
if not exist ".venv" python -m venv .venv
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt 2>nul
if not exist "input_papers" mkdir input_papers
if not exist "output" mkdir output
if not exist "logs" mkdir logs
python scripts\run_pipeline.py %*
echo.
echo Done! Upload SKILL.md + output\SESSION.md to any LLM.
