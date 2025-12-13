@echo off
echo Starting Real-Time Excel Monitor...
echo.
echo This will watch your Excel file and automatically update results when you save changes.
echo Press Ctrl+C to stop monitoring.
echo.
python -m pip install watchdog --quiet
python prediction_model/realtime_monitor.py
pause
