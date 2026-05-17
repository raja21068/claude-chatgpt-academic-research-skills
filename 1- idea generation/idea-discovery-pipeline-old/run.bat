@echo off
REM ── Idea Discovery Pipeline — Windows launcher ─────────────────────────────
REM Usage:
REM   run.bat                     Full pipeline
REM   run.bat --checkpoint        Pause for human review
REM   run.bat --resume            Resume after checkpoint
REM   run.bat --skip-embeddings   No ML deps
REM   run.bat --lite              Skip embeddings + quality (fastest)
REM ────────────────────────────────────────────────────────────────────────────

cd /d "%~dp0"

set ARGS=%*
if "%ARGS%"=="%ARGS:--lite=%" goto :noLite
set ARGS=%ARGS:--lite=--skip-embeddings --no-quality%
:noLite

REM Load .env
if exist .env (
    echo Loading .env...
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if not "%%A"=="" if not "%%A:~0,1%"=="#" set "%%A=%%B"
    )
)

REM Check API key
if "%ANTHROPIC_API_KEY%"=="" (
    echo ERROR: ANTHROPIC_API_KEY not set.
    echo   1. Copy .env.example to .env
    echo   2. Add your key
    echo   3. Run again
    exit /b 1
)

REM Setup venv
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

REM Install deps
echo Checking dependencies...
pip install -q -r requirements.txt 2>nul

REM Create dirs
if not exist "input_papers" mkdir input_papers
if not exist "output" mkdir output
if not exist "logs" mkdir logs

REM Run
echo.
python scripts\run_pipeline.py %ARGS%
