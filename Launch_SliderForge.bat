@echo off
cd /d "%~dp0"
python sliderforge.py
if errorlevel 1 pause
