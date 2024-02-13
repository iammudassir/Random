@echo off

:LOOP
cls
echo Press Ctrl+C to stop the loop.
timeout /nobreak /t 300 >nul
goto LOOP
