@echo off
cd /d "%~dp0"
python SliderForge.py
if errorlevel 1 pause
