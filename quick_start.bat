@echo off
echo ========================================
echo   Physiology MCQ Quiz - Quick Start
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
echo.

echo Step 2: Checking for MCQ data...
if exist mcqs_data.json (
    echo MCQ data found!
) else (
    echo No MCQ data found. Using sample data...
    copy sample_mcqs_data.json mcqs_data.json
    echo.
    echo To extract from your PDF, run:
    echo   python extract_mcqs_improved.py
)
echo.

echo Step 3: Starting web application...
echo.
echo The quiz will open at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
